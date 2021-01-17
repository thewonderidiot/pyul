import copy
from yul_system.types import Bit, SwitchBit, FieldCodBit, HealthBit, LocStateBit, \
                             MemType, Symbol, ALPHABET, ONES

class POPO:
    def __init__(self, health=0, card=''):
        self.health = health
        self.card = card

        vert_format = ord(self.card[7])
        if vert_format >= 0x50:
            vert_format -= 0x20
            self.seq_break = True
        else:
            self.seq_break = False

        if vert_format >= 0x40:
            self.marked = True
        else:
            self.marked = False

    def mark(self):
        if not self.marked:
            vert_format = ord(self.card[7])
            self.card = self.card[:7] + chr(vert_format + 0x10) + self.card[8:]
            self.marked = True

    def unmark(self):
        if self.marked:
            vert_format = ord(self.card[7])
            self.card = self.card[:7] + chr(vert_format - 0x10) + self.card[8:]
            self.marked = False

    def set_seq_break(self):
        if not self.seq_break:
            vert_format = ord(self.card[7])
            self.card = self.card[:7] + chr(vert_format + 0x20) + self.card[8:]
            self.seq_break = True

    def clear_seq_break(self):
        if self.seq_break:
            vert_format = ord(self.card[7])
            self.card = self.card[:7] + chr(vert_format - 0x20) + self.card[8:]
            self.seq_break = False

    def cardno_wd(self):
        return self.card[0:8]

    def loc_field(self):
        return self.card[8:16]

    def op_field(self):
        return self.card[16:24]

    def address_1(self):
        return self.card[24:32]

    def address_2(self):
        return self.card[32:40]

    def date_word(self):
        return self.card[64:72]

class BadMemory(Exception):
    pass

class IllegalOp(Exception):
    pass

class Disaster(Exception):
    pass

class BadMerge(Exception):
    pass

class Pass1:
    def __init__(self, mon, yul):
        self._mon = mon
        self._yul = yul
        self._real_cdno = 0
        self._last_cdno = 0
        self._field_cod = [None, None]
        self._end_of = POPO(health=0, card='⌑999999Q' + '%-72s' % yul.old_line)
        self._early = True
        self._op_found = None
        self._send_endo = False
        self._renum_disabled = False
        self._restart_log = False
        self._log_renum = False
        self._loc_state = 0
        self._renumber = 0
        self._sypt = None
        self._head = ' '
        self._end_yul = 'END YUL PASS 1'
        self._xforms = [
            0x4689A5318F,
            0x47BCDF42E2,
            0x47BCDF42E2,
            0xB7BCD642B4,
            0xB7BCD742B4,
            0x07BCDF62FF,
            0x37BCDF42B7,
            0x37BCDF42B7,
            0x1BBEEFB2BB,
            0x3CECEFC2EC,
            0x3DEEDFD2ED,
            0x1BBEEFB2BB,
            0x3CECEFC2EC,
            0x3DEEDFD2ED,
            0x1EEEEFE2EE,
            0x1FFFFFF2FF,
        ]


    def post_spec(self):
        if self._yul.switch & SwitchBit.SUBROUTINE:
            self._loc_ctr = self.subr_loc
        else:
            self._loc_ctr = ONES

        return self.get_real()

    def get_real(self):
        # Get real is normally the chief node of pass 1. Occasionally merge control procedures take
        # over, accepting or rejecting tape cards.
        try:
            while True:
                # Get a card and branch on no end of file.
                card = self.get_card()
                if card is None:
                    self._real = self._end_of
                    return self.tp_runout()

                if self._yul.switch & SwitchBit.MERGE_MODE:
                    if not self._yul.switch & SwitchBit.TAPE_KEPT:
                        self._tape = self.get_tape()

                        if self._tape is None:
                            # FIXME: Clean up and exit pass 1
                            return

                self.modif_chk()
        except BadMerge:
            return self.bad_merge()

    def tp_runout(self):
        if not self._yul.switch & SwitchBit.MERGE_MODE:
            self.proc_real()

        if self._yul.switch & SwitchBit.TAPE_KEPT:
            self.proc_tape()

        self._tape = self.get_tape()
        while self._tape is not None:
            self.proc_tape()
            self._tape = self.get_tape()

        return self.end_pass_1()

    def end_pass_1(self):
        if self._yul.popos[-1].health != 0:
            print(self._yul.popos[-1].card)
            raise Disaster()

        if self._yul.switch & SwitchBit.FREEZE_P1:
            self.send_popo(self._end_of)

        # FIXME: play with number of copies?

        bad1_bits = (SwitchBit.REPRINT |
                     SwitchBit.SUPPRESS_INACTIVE | SwitchBit.SUPPRESS_SYMBOL | SwitchBit.SUPPRESS_OCTAL | 
                     SwitchBit.CONDISH_INACTIVE  | SwitchBit.CONDISH_SYMBOL  | SwitchBit.CONDISH_OCTAL)

        # Maybe set reprint flag for passes 1.5, 3.
        self._yul.switch &= ~SwitchBit.REPRINT_PASS1P5
        if self._yul.switch & SwitchBit.REPRINT:
            self._yul.switch |= SwitchBit.REPRINT_PASS1P5

        # Branch on no merge error.
        if self._end_yul.endswith('≠'):
            # Bar YULPROGS writes, bar some printing.
            self._yul.switch |= bad1_bits

        self._mon.mon_typer(self._end_yul)

        # Clear out substrand (paragraph) table
        self._yul.substrab = [False]*256

        # FIXME: do segment things

        comp_pass2 = self._mon.phi_load(self._yul.comp_name + '.PASS2', self._yul, self.adr_limit, self.m_typ_tab)
        if comp_pass2 is None:
            self._yul.typ_abort()

        return comp_pass2.pass_1p5()

    def get_card(self):
        # Subroutine in pass 1 to get a real card. Normally performs card number checking. Response
        # to Yul director or monitor card (end of file situations) is to peek only.

        # Peek at card.
        card = self._mon.mon_peek()

        # Branch if not any kind of end of file.
        if card[0] in 'Y*':
            if card[0] == 'Y':
                # Show that another task follows.
                self._yul.switch |= SwitchBit.ANOTHER_TASK

            # End of file exit after peek at mon card.
            self._real_cdno = Bit.BIT6
            return None

        # See no input if reprinting.
        if self._yul.switch & SwitchBit.REPRINT:
            return None

        card = self._mon.mon_read()
        self._real = POPO(health=0, card=card)

        if self._real.card[7] == ' ':
            # Insert upspace 1 for blank.
            self._real.card = self._real.card[:7] + '1' + self._real.card[8:]

        elif self._real.card[7] == '-':
            # Assume minus is a fat-fingering of 2.
            self._real.card = self._real.card[:7] + '2' + self._real.card[8:]

        elif not self._real.card[7].isnumeric():
            # Insert form-skip for non-numeric.
            self._real.card = self._real.card[:7] + '8' + self._real.card[8:]

        # Mark all cards entering during merging.
        if self._yul.switch & SwitchBit.MERGE_MODE:
            self._real.mark()

        # Blot out undesirable column 1 contents.
        if not (self._real.card[0].isalnum() or self._real.card[0] in '= '):
            self._real.card = '■' + self._real.card[1:]

        self._real.health = 0

        # Card number sequence checking and sequence break analysis.

        # Isolate card no. for seq. brk. analysis.
        card_no = self._real.card[1:7]

        # Substitute zero for blank.
        card_no = card_no.replace(' ', '0')

        seq_break = False
        test_col1 = True

        if not card_no.isnumeric():
            # "SEQBRK" is only non-numeric allowed.
            if card_no == 'SEQBRK':
                seq_break = True

            # Allow for "LOG" in col 2-7 of acceptor.
            elif self._real.card[0] == '=':
                seq_break = True

            # Show illegal number field by zero.
            else:
                card_no = '000000'

        # Card number 999999 is a sequence break.
        if card_no == '999999':
            seq_break = True

        # Do not test column 1 of right print.
        if self._real.card[7] != '9':
            # A log card is an automatic sequence break.
            if self._real.card[0] == 'L':
                # FIXME: Remove confusing info from log card?
                # self._real.card = self._real.card[0] + '      ' + self._real.card[7:]
                seq_break = True

            # Branch if not TINS (Tuck In New Section)... which is an incipient log card.
            if self._real.card[0] == 'T':
                seq_break = True

            # Op code "MODIFY" is automatic seq. brk.
            if self._real.card[0] == ' ' and self._real.card[16:22] == 'MODIFY':
                seq_break = True

        if seq_break:
            # Insert sequence break bit in card.
            self._real.set_seq_break()

            # Set up criterion after sequence break.
            self._real_cdno = Bit.BIT6
            return self._real.card

        real_card_no = int(card_no, 10)

        if real_card_no <= (self._real_cdno & 0xFFFFFFFFF):
            # Disorder
            self._real.health |= Bit.BIT7

        # Keep normal form of card number on tape.
        self._real.card = self._real.card[0] + card_no + self._real.card[7:]

        self._real_cdno = real_card_no
        return self._real.card

    def send_popo(self, popo):
        if self._renum_disabled:
            # Restore renumbering test to normal.
            self._renum_disabled = False
            return self.move_popo(popo)

        # Branch if renumbering is on.
        if not (self._yul.switch & SwitchBit.RENUMBER):
            return self.move_popo(popo)

        # Go to renumber most card types.
        card_type = popo.health & HealthBit.CARD_TYPE_MASK
        if card_type >= HealthBit.CARD_TYPE_RIGHTP:
            return self.rnum_card(popo)

        # Br if merge control or merge error card.
        if card_type != HealthBit.CARD_TYPE_REMARK:
            # Branch if merge control card.
            if HealthBit.CARD_TYPE_CARDNO > card_type:
                # Shut off renumbering on bad merge.
                self._yul.switch &= ~SwitchBit.RENUMBER

            return self.move_popo(popo)

        # Branch to renumber non-log remarks.
        if popo.card[0] != 'L':
            return self.rnum_card(popo)

        # Restart number sequence after log etc.
        self._field_cod[1] = 0
        self._renumber = 0
        if self._restart_log:
            self._yul.switch &= ~SwitchBit.RENUMBER

        return self.move_popo(popo)

    def rnum_card(self, popo):
        # Wipe out obsolete sequence error bit.
        popo.health &= ~Bit.BIT7

        if self._renumber > 999898:
            # Generate seqbreak after card 9998.98.
            popo.set_seq_break()
            popo.card = popo.card[0] + 'SEQBRK' + popo.card[7:]
            self._renumber = 0
            self._field_cod[1] = 0
            return self.move_popo(popo)

        self._renumber += 100

        # Erase old sequence break flag.
        popo.clear_seq_break()

        # Plant it and go to move card.
        self._field_cod[1] = self._renumber
        popo.card = popo.card[0] + ('%06d' % self._renumber) + popo.card[7:]

        return self.move_popo(popo)

    def move_popo(self, popo):
        self._yul.popos.append(popo)

    def modif_chk(self):
        # See if operation code of real card is "MODIFY". But don't be fooled by a remarks card.
        if self._real.card[1:6] == 'MODIFY' and self._real.card[0] == ' ' and (ord(self._real.card[7]) & 0xF) != 9:
            # Indicate card type.
            self._real.health |= HealthBit.CARD_TYPE_MODIFY
            if not self._yul.switch & SwitchBit.MERGE_MODE:
                # When in main part of new program send the "MODIFY" card, create and send the
                # "END OF" card made up by pass 0, and process the latter.
                self.proc_real()
                self._real = self._end_of
                self.proc_real()
                return

            # Set up search for "END OF" card.
            while self._tape.card[:8] != self._end_of[:8]:
                self.proc_tape()

                # Get another tape card if not found yet.
                self._tape = self.get_tape()
                if self._tape is None:
                    raise Disaster()

            # Process "MODIFY" just before "END OF".
            self.proc_real()
            return self.proc_tape()

        if not self._yul.switch & SwitchBit.MERGE_MODE:
            # Process real card with no further ado.
            return self.proc_real()

        return self.comp_cdns()

    def comp_cdns(self):
        # COMP CDNS is the heart of the merging process. If the tape card is chosen,
        # it cannot be an "END OF" card.
        while True:
            if self._real_cdno <= self._tape_cdno:
                break

            # Since the last card of a tape file is numered 999999, we guarantee no EOF.
            self.proc_tape()
            self._tape = self.get_tape()

        return self.keep_tape()

    def keep_tape(self):
        # Indicate that a tape card is waiting.
        self._yul.switch |= SwitchBit.TAPE_KEPT

        # Right print can't be merge control card.
        if (ord(self._real.card[7]) & 0xF) == 9:
            return self.not_mccd()

        # Branch if not an acceptor card.
        if self._real.card[0] != '=':
            return self.not_acept()

        # Reject if disordered card number.
        self._real.health |= HealthBit.CARD_TYPE_ACCEPT
        if (self._real.health >> 36) & 0o77:
            raise BadMerge()

        # Analyze card number field.
        common, value = self.anal_subf(self._real.cardno_wd()[1:7], self._real)
        common = common.strip()

        # Disable complaint about "D" error.
        self._real.health &= ~Bit.BIT9

        # Branch if not accepting a log card.
        merj_rtrn = False
        if common == "LOG":
            # Branch if dashes should be put in date.
            if self._real.card[67:69] != '  ' or self._real.card[70:72] != '  ':
                self._real.card = self._real.card[:69] + '-' + self._real.card[70:72] + '-' + self._real.card[73:]
            merj_rtrn = True

        while True:
            # Illegal to accept an "END OF" card thus.
            if self._tape.cardno_wd() == self._end_of.cardno_wd():
                raise BadMerge()

            if ((self._tape_cdno != self._real_cdno) or         # Demand equality of formal card number.
                (merj_rtrn and self._tape.card[0] != 'L') or    # Branch if tape card should be log.
                (self._tape.card[8:] != self._real.card[8:]) or # Branch if difference in cols. 9-80.
                (self._tape.card[0] == 'L' and not merj_rtrn)): # Branch if log but should not be.
                # Accept a card and get another.
                self.proc_tape()
                self._tape = self.get_tape()
                continue

            break

        # Mark card as accepted.
        self._tape.mark()

        # Send acceptor card.
        self.send_popo(self._real)

        # Process accepted card, get another real.
        self.proc_tape()

    # Procedure to detect and process requests for changing or correcting card numbers, using the "CARDNO" code. The
    # "CARDNS" code is similar, but starts renumbering from that value until the next log card. "PRESERVE CDNS"
    # turns off renumbering. If "RENUMBER" subdirector was used, it resumes after the reign of any "CARDNS" code.
    def not_acept(self):
        # Branch if cannot be merge control card.
        if self._real.card[0] != ' ':
            return self.not_mccd()

        # Branch if not a "CARDNS" code.
        if self._real.card[17:23] != 'CARDNS':
            return self.cardno_cq()

        if self._real.loc_field() != 'PRESERVE':
            return self.cardno_cq(cardns=True)

        self._real.health |= HealthBit.CARD_TYPE_CARDNO
        if (not self._real.address_1().isspace()) or (not self._real.address_1().isspace()):
            # Cuss bad address field.
            self._real.health |= Bit.BIT9
            raise BadMerge()

        # Reject "PRESERVE CARDNS" for any defect.
        if self._real.health & ~HealthBit.CARD_TYPE_MASK:
            raise BadMerge()

        self.find_cdno()

        # Exit quietly if renumbering already off.
        if self._yul.switch <= Bit.BIT1:
            self.send_popo(self._real)
            return self.proc_tape()

        # Branch if preservation causes disorder.
        if self._real_cdno <= self._field_cod[1]:
            self._real.health |= Bit.BIT7
            raise BadMerge()

        self._yul.switch &= ~SwitchBit.RENUMBER

        # Exit if renumbering was in log sec only.
        if not self._restart_log:
            # Modify log card routine to start renum.
            self._log_renum = True

        self.send_popo(self._real)
        return self.proc_tape()

    def cardno_cq(self, cardns=False):
        # Branch if not a "CARDNO" code.
        if (not cardns) and (self._real.card[17:23] != 'CARDNO'):
            return self.delete_cq()

        # Analyze location field.
        common, value = self.anal_subf(self._real.loc_field(), self._real)
        common = common.strip()
        if common == 'CORRECT':
            # Set up search for bad card number if "CORRECT" but never cuss this card no.
            self._yul.switch |= SwitchBit.CORRECT
            self._real.health = 0
        elif common == 'CHANGE':
            # Seek OK card number if "CHANGE".
            self._yul.switch &= ~SwitchBit.CORRECT
        else:
            # Cuss bad location field.
            self._real.health |= Bit.BIT8

        # Note type, analyze address field.
        self._real.health |= HealthBit.CARD_TYPE_CARDNO
        cn_limit = self.mccd_adrf()

        if self._field_cod[0] != Bit.BIT2:
            # Cuss bad address field.
            self._real.health |= Bit.BIT9
            raise BadMerge()

        # Reject "CARDNO" for any sin.
        if self._real.health & ~HealthBit.CARD_TYPE_MASK:
            raise BadMerge()

        # Set up card whose number is to be chgd.
        self.find_cdno()

        # Change external card number.
        self._tape.card = self._tape.card[0] + ('%06d' % cn_limit) + self._tape.card[7:]
        self._tape.mark()

        # On log card, change is superficial only.
        if self._tape.card[0] == 'L':
            if self._tape.card[1:7] != '000000':
                return self.send_ccno()
            # ..though SQB setting is blanked.
            self._tape.card = self._tape.card[0] + '      ' + self._tape.card[7:]
            return self.send_ccno()

        # Clear possible sequence break bit.
        self._tape.clear_seq_break()

        # Change internal card number.
        self._tape_cdno = cn_limit

        # If seq. br., set external card number to SEQBRK and set bit 43.
        if self._tape_cdno == Bit.BIT6:
            self._tape.card = self._tape.card[0] + 'SEQBRK' + self._tape.card[7:]
            self._tape.set_seq_brk()

        return self.send_ccno()

    def send_ccno(self):
        # Send "CARDNO", "CARDNS", or "DELETE".
        self.send_popo(self._real)

        # Branch if a section was renumbered.
        if self._real.card[17:23] == 'CARDNO':
            # New number is criterion for next real.
            self._real_cdno = self._tape_cdno
            # Process accepted card, get another real.
            return self.proc_tape()

        # If renumber is now under way, compare new number with last card's renumber.
        if self._yul.switch & SwitchBit.RENUMBER:
            self._last_cdno = self._field_cod[1]

        # Process card with renumbering disabled.
        self._renum_disabled = True
        self.proc_tape()

        self._renumber = self._last_cdno

        # For CARDNS, keep old sequence criterion.
        self._last_cdno = self._real_cdno

        # Exit if renumbering is now under way.
        if self._yul.switch & SwitchBit.RENUMBER:
            return

        # Call for partial renumbering.
        self._yul.switch |= SwitchBit.RENUMBER

        # Make it stop after first log card.
        self._restart_log = True
        return

    # Proceudre to detect and process "DELETE" cards.
    def delete_cq(self):
        # Branch if not a "CARDNO" code.
        if self._real.card[17:23] != 'DELETE':
            return self.insert_cq()

        # Branch if location field not "OUTOFSEQ".
        if self._real.loc_field() == 'OUTOFSEQ':
            # Set up search for bad card number.
            self._yul.switch |= SwitchBit.CORRECT

            # Never cuss this card number.
            self._real.health = 0
        else:
            # Cuss bad location field.
            if not self._real.loc_field().isspace():
                self._real.health |= Bit.BIT8

            # Set up search for OK card number.
            self._yul.switch &= ~SwitchBit.CORRECT

        # Analyze address field.
        self._real.health |= HealthBit.CARD_TYPE_DELETE
        cn_limit = self.mccd_adrf()

        # Branch if address field not blank.
        if self._field_cod[0] == 0:
            # Reject singleton delete for bad card no.
            if self._real.health & ~HealthBit.CARD_TYPE_MASK:
                self._real_cdno = self._last_cdno
                raise BadMerge()

            # Go find single card to be deleted.
            self.find_cdno()
        else:
            if self._field_cod[0] != Bit.BIT1:
                # Cuss bad address field.
                self._real.health |= Bit.BIT9
                self._real_cdno = self._last_cdno
                raise BadMerge()

            # Branch if first cardno is not seq break.
            if self._real_cdno != Bit.BIT6:
                # Cuss if 1st cardn not less than 2nd.
                if self._real_cdno >= cn_limit:
                    self._real.health |= Bit.BIT12
                    self._real_cdno = self._last_cdno
                    raise BadMerge()
            else:
                # Branch if 2nd cardno is not seq break.
                if cn_limit == Bit.BIT6:
                    self._real.health |= Bit.BIT12
                    self._real_cdno = self._last_cdno
                    raise BadMerge()

            # Reject "DELETE" card for any sin.
            if self._real.health & ~HealthBit.CARD_TYPE_MASK:
                self._real_cdno = self._last_cdno
                raise BadMerge()

            # Set up card to be deleted.
            self.find_cdno()

            # Fetch next card to look at number.
            while True:
                self._tape = self.get_tape()
                if cn_limit <= self._tape_cdno:
                    break

            # Second number must match existing one.
            if cn_limit != self._tape_cdno:
                self._real.health |= Bit.BIT11
                self._real_cdno = self._last_cdno
                raise BadMerge()

        # Send "DELETE" card.
        self._real_cdno = self._last_cdno
        self.send_popo(self._real)

        # Allow deletion of any but "END OF" card.
        if self._tape.cardno_wd() == self._end_of.cardno_wd():
            # Keep it and maybe insert before it.
            self._yul.switch |= SwitchBit.TAPE_KEPT
        else:
            # End of deletion process.
            self._yul.switch &= ~SwitchBit.TAPE_KEPT

    # Procedure to detect and process "INSERT" cards.
    def insert_cq(self):
        if self._real.card[17:23] != 'INSERT':
            return self.not_mccd()

        # FIXME
        pass

    # Common procedure when merging is given up for lost for any reason.
    def bad_merge(self):
        # Send bad merge control card.
        self.send_popo(self._real)

        # Type most guilty card.
        self._real.card = self._real.card[:7] + ' ' + self._real.card[8:]
        self._mon.mon_typer(self._real.card)

        # Announce rejection of task.
        self._real = POPO(health=HealthBit.CARD_TYPE_ENDERR,
                          card='E■■■■■■ATHIS TASK IS REJECTED. RESUBMIT CORRECTED DECK WITH SAME DIRECTOR CARD. ')
        self.send_popo(self._real)

        # Loop to accept remaining tape cards.
        while self._tape is not None:
            self.proc_tape()
            self._tape = self.get_tape()

        # See whether to throw out remaining real cards, eing careful not to announce
        # same if there are none.
        self.get_card()
        if self._real is not None:
            # FIXME: HEAVE HO
            pass

        self._end_yul += ' ≠'
        return self.end_pass_1()

    # Subroutine in pass 1 to find the tape card to which a merge control card refers.
    # Exits to BAD MERGE if no exact card number match is found before a sequence break.
    def find_cdno(self):
        while True:
            # Branch if tape card not sequence break.
            if self._tape_cdno == Bit.BIT6:
                # Always illegal to find an "END OF" card. Branch if real card not sequence break.
                if self._tape.cardno_wd() == self._end_of.cardno_wd() or self._tape_cdno != self._real_cdno:
                    # Cuss failure to find match.
                    self._real.health |= Bit.BIT10
                    raise BadMerge()

                # Branch if not seeking bad card number.
                if not self._yul.switch & SwitchBit.CORRECT:
                    return

                # Cuss illegal location field.
                self._real.health |= Bit.BIT8
                raise BadMerge()

            # Branch if no match yet.
            if self._tape_cdno == self._real_cdno:
                # Branch if looking for bad card number and desired bad card no. found.
                if self._yul.switch & SwitchBit.CORRECT:
                    if self._tape.health != 0:
                        return

                # Bad card number implies no match.
                elif self._tape.health == 0:
                    return

            # Process a tape card and look again
            self.proc_tape()
            self._tape = self.get_tape()

    # We get to NOT MCCD for every real card that is not a merge control card.
    def not_mccd(self):
        if self._real.health > 0:
            # Card no. error in revision cards is bad.
            self._real.health |= HealthBit.CARD_TYPE_ENDERR
            raise BadMerge()

        # Branch if real card precedes tape card.
        if self._real_cdno != self._tape_cdno:
            return self.proc_real()

        # Force same if real card is "TUCK-IN".
        if self._real.card[0] == 'T':
            self._real.card = 'L' + self._real.card[1:]
            return self.proc_real()

        # Force same if tape card is "END OF".
        if self._tape.cardno_wd() == self._end_of.cardno_wd():
            return self.proc_real()

        # Otherwise replace tape card with real.
        self._yul.switch &= ~SwitchBit.TAPE_KEPT
        return self.proc_real()

    def proc_real(self):
        return self.process(self._real, self._real_cdno)

    def proc_tape(self):
        # Unkeep and process tape card.
        self._yul.switch &= ~SwitchBit.TAPE_KEPT
        return self.process(self._tape, self._tape_cdno)

    def process(self, popo, cdno):
        # Final sequence checking before processing.
        if (cdno <= self._last_cdno) and (cdno != Bit.BIT6):
            # Indicate card number out of sequence.
            popo.health |= Bit.BIT7
        else:
            # Clear possible error bit, tab to exit.
            popo.health &= ~Bit.BIT7

        self._last_cdno = cdno & ~Bit.BIT6

        if (ord(popo.card[7]) & 0xF) == 9:
            popo.health |= HealthBit.CARD_TYPE_RIGHTP
            return self.send_popo(popo)

        if popo.card[0] == 'R':
            popo.health |= HealthBit.CARD_TYPE_REMARK
            return self.send_popo(popo)

        if popo.card[0] == 'A':
            popo.health |= HealthBit.CARD_TYPE_ALIREM
            return self.send_popo(popo)

        if popo.card[0] == 'P':
            popo.health |= HealthBit.CARD_TYPE_REMARK
            return self.send_popo(popo)

        if popo.card[0] == 'L':
            if self._log_renum:
                self._log_renum = False
                self._yul.switch |= SwitchBit.RENUMBER

            # Branch if dashes should be put in date.
            if popo.card[67:69] != '  ' or popo.card[70:72] != '  ':
                popo.card = popo.card[:69] + '-' + popo.card[70:72] + '-' + popo.card[73:]

            # FIXME: Send a dummy acceptor ahead of a marked log card entering as a member of a called subro
            popo.health |= HealthBit.CARD_TYPE_REMARK
            return self.send_popo(popo)

        # Check for "END OF" information from tape or (new program or subro) from pass 0.
        if popo.cardno_wd() == self._end_of.cardno_wd():
            popo.health |= HealthBit.CARD_TYPE_END_OF
            return self.end_of(popo)

        op_field = popo.op_field()[1:7]

        if self._early:
            if op_field == 'MEMORY':
                return self.memory(popo)

            if op_field == 'SEGNUM':
                return self.segnum(popo)

            self._early = False

        common, value = self.anal_subf(op_field, popo)
        operation = common.strip()

        try:
            if self._field_cod[0] is None:
                raise IllegalOp()

            elif self._field_cod[0] in (0, FieldCodBit.SYMBOLIC):
                if operation != '' and operation[-1] == '*':
                    popo.health |= HealthBit.ASTERISK
                    operation = operation[:-1]

                if operation in self.op_thrs:
                    if isinstance(self.op_thrs[operation], int):
                        opcode = self.op_thrs[operation] & ~Bit.BIT37
                        if self._op_found is None:
                            popo.health |= (opcode << 16)
                        else:
                            self._op_found(popo, opcode)
                        popo.health |= HealthBit.CARD_TYPE_INSTR
                    else:
                        self.op_thrs[operation](popo)
                        return
                else:
                    raise IllegalOp()

            elif not self._field_cod[0] & FieldCodBit.UNSIGNED:
                raise IllegalOp()

            else:
                popo.health |= (value << self.mod_shift)
                if value <= self.max_num_op:
                    popo.health |= HealthBit.CARD_TYPE_INSTR
                else:
                    raise IllegalOp()

        except IllegalOp:
            return self.illegop(popo)

        return self.inst_dec_oct(popo)

    def end_of(self, popo):
        if not self._send_endo:
            self._send_endo = True
            # The subroutines are known.
            self._yul.switch |= SwitchBit.KNOW_SUBS
            # Prohibit renumbering in subroutines.
            self._yul.switch &= ~SwitchBit.RENUMBER

            # FIXME: set up first subro

            # Prevent false alarms in rejection.
            self._real_cdno = 0

            # Use existing "END OF" card for reprint.
            if (not (self._yul.switch & SwitchBit.REPRINT)) and (self._yul.switch & SwitchBit.MERGE_MODE):
                # When revising, first "END OF" card must be replaced by the one made by pass 0.
                popo.card = self._end_of.card

        # FIXME: set up next subro

        # Exit via SEND POPO unless freezing subs.
        if not self._yul.switch & SwitchBit.FREEZE:
            return self.send_popo(popo)

    def illegop(self, popo):
        self._yul.switch &= ~(Bit.BIT25 | Bit.BIT26 | Bit.BIT27)
        self._yul.switch |= MemType.FIXED
        self._loc_state = 0
        self.location(popo, blank=True)
        popo.health &= ~HealthBit.CARD_TYPE_MASK
        popo.health |= HealthBit.CARD_TYPE_ILLOP
        return self.reg_incon(popo, translate_loc=False)


    def inst_dec_oct(self, popo):
        self._yul.switch &= ~MemType.MEM_MASK
        self._yul.switch |= MemType.FIXED
        if popo.card[0] == 'J':
            # FIXME: handle leftovers
            translate_loc = False
        else:
            translate_loc = True

        return self.reg_incon(popo, translate_loc)

    def reg_incon(self, popo, translate_loc=True):
        if translate_loc:
            self._loc_state = 0
            self.location(popo)
        popo.health |= self._loc_state
        return self.send_popo(popo)

    def location(self, popo, blank=False):
        self._field_cod[1] = None
        symbol = None
        new_health = 0

        # Initialize transform address
        sym_xform = self._xforms[0]

        if not blank:
            # Analyze location field.
            common, value = self.anal_subf(popo.loc_field(), popo)
            if self._field_cod[0] == FieldCodBit.SYMBOLIC:
                # Signal symbolic loc.
                self._loc_state |= LocStateBit.SYMBOLIC

                # Aanalyze history of symbol.
                sym_name = common.strip()
                symbol = self.anal_symb(sym_name)

                if symbol is None:
                    # symbol is None if sym tab full.
                    self._loc_state |= LocStateBit.FULL
                    # In which case treat loc as blank.
                else:
                    # Using old symbol health as rel address, get address of transform word.
                    sym_xform = self._xforms[symbol.health]
                    new_health = (sym_xform >> 8*4) & 0xF

            elif self._field_cod[0] != None:
                if self._field_cod[0] & FieldCodBit.UNSIGNED:
                    self._field_cod[1] = self._loc_ctr
                    self._loc_ctr = value

        loc_value = self._loc_ctr
        if self.incr_lctr():
            self._field_cod[1] = None

        if loc_value > self.max_loc:
            self._loc_ctr = ONES
            # Signal oversize.
            self._loc_state |= LocStateBit.OVERSIZE
            # Use oversize transform on symbol health.
            new_health = (sym_xform >> 7*4) & 0xF
            loc_value = 0
            if self._field_cod[1] is not None:
                self._loc_ctr = self._field_cod[1]
                loc_value = self._loc_ctr
                self.incr_lctr()
            self.loc_exit(loc_value, symbol, new_health)
        else:
            self.ok_l_size(loc_value, symbol, sym_xform, new_health)

    def loc_exit(self, loc_value, symbol, new_health):
        self._loc_state |= loc_value
        if self._loc_state & LocStateBit.SYMBOLIC:
            self.sy_def_xit(loc_value, symbol, new_health)

    def sy_def_xit(self, loc_value, symbol, new_health):
        if symbol is None:
            return False

        # Branch if this is the only definition.
        if symbol.health == 0:
            symbol.value = loc_value
            symbol.health = new_health
            return

        symbol = copy.deepcopy(symbol)
        symbol.value = loc_value
        symbol.health = new_health

        sym_fit = self._yul.sym_thr.add(symbol)
        if not sym_fit:
            # Location-symbol-didn't-fit-in-table-flg.
            self._loc_state |= Bit.BIT17

    def ok_l_size(self, loc_value, symbol, sym_xform, new_health):
        # Look up memory type.
        midx = 0
        while loc_value > self.m_typ_tab[midx][1]:
            midx += 1
        mem_type = self.m_typ_tab[midx][0]

        bad = False
        # Branch if type doesn't match that suplyd.
        if (self._yul.switch & MemType.MEM_MASK) != mem_type:
            new_health = (sym_xform >> 6*4) & 0xF
            self._loc_state |= LocStateBit.WRONG_TYPE
            if self._field_cod[1] is not None:
                self._loc_ctr = self._field_cod[1]
                loc_value = self._loc_ctr
                self.incr_lctr()
            self.loc_exit(loc_value, symbol, new_health)
            return

        if sym_xform == self._xforms[5]:
            if symbol.value < 0:
                leftover_type = MemType.ERASABLE
            else:
                leftover_type = MemType.FIXED
            if (self._yul.switch & MemType.MEM_MASK) != leftover_type:
                new_health = (sym_xform >> 6*4) & 0xF

        if not self.avail(loc_value, reserve=True):
            new_health = (sym_xform >> 5*4) & 0xF
            self._loc_state |= LocStateBit.CONFLICT

        self.loc_exit(loc_value, symbol, new_health)

    def avail(self, loc_value, reserve=False):
        available = True

        avail_msk = 1 << (loc_value & 0x1F)
        avail_idx = loc_value >> 5

        if self._yul.av_table[avail_idx] & avail_msk:
            available = False

        if reserve:
            self._yul.av_table[avail_idx] |= avail_msk

        return available

    def incr_lctr(self):
        if self._loc_ctr >= ONES:
            return False
        self._loc_ctr += 1
        return True

    # Subroutine in pass 1 to break down the address field of a merge control card. That is, with an op
    # code of "CARDNO" or "DELETE". Uses the sentence reader. Sets up FIELDCOD and CNLIMIT as follows:
    # FIELD ALL BLANK        FIELDCOD=0
    # "THROUGH" WITH NUMBER  FIELDCOD=B1, CNLIMIT=NUMBER
    # "THRU"    WITH NUMBER  FIELDCOD=B1, CNLIMIT=NUMBER
    # "TO"      WITH NUMBER  FIELDCOD=B2, CNLIMIT=NUMBER
    # "WITH"    WITH NUMBER  FIELDCOD=B3, CNLIMIT=NUMBER
    # The n number in the address field may be "SEQBREAK" or "SEQBRK" causing CNLIMIT to become ALF 10000000, or up ot 6
    # decimal digits with an optional decimal point. If the number is present, there may be up to four digits to its
    # left and up to two digits to its right. If the point is absent and there are four digits or less, the point is
    # assumed to be at their immediate right. If the point is absent and there are five or six digits, the point is
    # assumed to follow the fourth digit. At least one blank or other terminator must separate the two subfields, but
    # no imbedded blanks are allowed in either subfield.  If any of these rules are violated or there is a third
    # subfield, FIELDCOD is set to all ones and the card is ignored and cussed at for a meaningless address field.
    # The number set up in CNLIMIT is a standardized to six digits thus: ALF 0NNNNNN0, with a point assumed after char5.
    def mccd_adrf(self):
        # Set up and call sentence reader.
        sentence = self._mon.phi_sentr(self._real.card[16:])
        if sentence[0] == '':
            # FIXME: Cuss if contains terminator only
            self._field_cod[0] = 0
            return None

        # FIXME: Cuss unwanted terminators.
        if sentence[0] in ('THRU', 'THROUGH'):
            # Signify THROUGH and go to find number.
            self._field_cod[0] = Bit.BIT1
        elif sentence[0] == 'WITH':
            # Signify WITH.
            self._field_cod[0] = Bit.BIT3
        elif sentence[0] == 'TO':
            # Signify TO.
            self._field_cod[0] = Bit.BIT2
        else:
            self._field_cod[0] = None
            return None

        if sentence[1] in ('SEQBREAK', 'SEQBRK'):
            # Exit when number is sequence break.
            return Bit.BIT6

        if sentence[1].isspace():
            # Bad exit when number is missing.
            self._field_cod[0] = None
            return None

        s3 = -5
        cn_limit = '000000'

        cardno = sentence[1] + ' '

        while True:
            # Branch if not a digit.
            if not cardno[0].isnumeric():
                break

            # Branch if this is the fifth digit.
            s3 += 1
            if s3 == 0:
                break

            # Move up previous digits. Plant a before-digit point.
            cn_limit = cn_limit[1:4] + cardno[0] + cn_limit[4:]

            # Move next character into position.
            cardno = cardno[1:]

        # If the fifth or earlier card is not a digit, it must be a decimal point or a blank.
        skip_digits = False
        if s3 != 0:
            if cardno[0] == '.':
                cardno = cardno[1:]
            elif cardno[0] != ' ':
                skip_digits = True

        if not skip_digits:
            # Plant first digit after point.
            if cardno[0].isnumeric():
                cn_limit = cn_limit[:4] + cardno[0] + cn_limit[5]
                cardno = cardno[1:]

            # Plant second digit after point.
            if cardno[0].isnumeric():
                cn_limit = cn_limit[:4] + cardno[0] + cn_limit[5]
                cardno = cardno[1:]

        # Bad exit if queer character. Bad exit if third subfield.
        if cardno[0] != ' ' or sentence[2] != '':
            self._field_cod[0] = None
            return None

        # Check for 999999 sequence break.
        if cn_limit == '999999':
            cn_limit = Bit.BIT6

        return int(cn_limit)

    def anal_symb(self, sym_name):
        if len(sym_name) < 8:
            # Append head if there is room
            sym_name = ('%-7s%s' % (sym_name, self._head)).strip()

        return self._yul.sym_thr[sym_name]

    def segnum(self, popo):
        # FIXME: IMPLEMENT SEGMENT ASSEMBLIES
        return self.send_popo(popo)

    def memory(self, popo):
        adr_wd = self.adr_field(popo)
        try:
            if self._field_cod[0] is None:
                raise BadMemory(Bit.BIT11)

            us_num = FieldCodBit.NUMERIC | FieldCodBit.UNSIGNED
            if (self._field_cod[0] & us_num) != us_num:
                raise BadMemory(Bit.BIT11)

            popo.health |= (adr_wd[0] << 16) & 0xFFFF0000
            if self._field_cod[1] == 0:
                adr_wd[1] = adr_wd[0]
            elif self._field_cod[1] & FieldCodBit.POSITIVE:
                adr_wd[1] = adr_wd[0] + adr_wd[1]
            elif adr_wd[0] > abs(adr_wd[1]):
                raise BadMemory(Bit.BIT11)

            low_lim = adr_wd[0]
            hi_lim = abs(adr_wd[1])

            if hi_lim >= self.adr_limit:
                raise BadMemory(Bit.BIT12)

            popo.health |= hi_lim & 0xFFFF

            common, value = self.anal_subf(popo.loc_field(), popo)
            m_name = common.strip()

            # Reject if not symbolic.
            if not self._field_cod[0] & FieldCodBit.SYMBOLIC:
                raise BadMemory(Bit.BIT8)

            if m_name == 'ERASABLE':
                # Attach erasable code to upper limit.
                mem_type = MemType.ERASABLE
            elif m_name == 'FIXED':
                # Attach fixed code to upper limit.
                mem_type = MemType.FIXED
            elif m_name == 'SPEC/NON':
                # Attach spec/non code to upper limit.
                mem_type = MemType.SPEC_NON
            else:
                # Reject ill-formed memory card.
                raise BadMemory(Bit.BIT8)

            low_idx = 0
            hi_idx = 0

            if low_lim == 0:
                # Does req cover all 1st present category.
                if hi_lim > self.m_typ_tab[0][1]:
                    # Put req type in 1st category.
                    self.m_typ_tab[0] = (mem_type, self.m_type_tab[0][1])
                else:
                    common = 0
                    # FIXME: go to CHECK TM1
            else:
                # Use reduced lower limit.
                low_lim -= 1

                # Find first category affected by request.
                while low_lim > self.m_typ_tab[low_idx][1]:
                    low_idx += 1

                hi_idx = low_idx
                # go to CHK HI LIM

            # Determine end of table.
            end_typ_ta = len(self.m_typ_tab) - 1

            # Search for last affected category.
            while (hi_idx < end_typ_ta) and (hi_lim >= self.m_typ_tab[hi_idx][1]):
                hi_idx += 1

            # Branch if request is non-trivial.
            if (low_idx == hi_idx) and (mem_type == self.m_typ_tab[low_idx][0]):
                popo.health |= HealthBit.CARD_TYPE_MEMORY
                return self.send_popo(popo)

            if hi_lim == self.m_typ_tab[end_typ_ta][1] and low_idx < hi_idx:
                self.m_typ_tab[hi_idx] = (mem_type, hi_lim)

            # Remove entries entirely spanned.
            obsolete = max(hi_idx - low_idx - 1, 0)
            for i in range(obsolete):
                self.m_typ_tab.pop(low_idx + 1)
                hi_idx -= 1

            if low_lim < self.m_typ_tab[low_idx][1] and mem_type != self.m_typ_tab[low_idx][0]:
                # First affected category is being shortened.
                if low_idx == hi_idx:
                    # The request splits the first category in two. Insert an entry corresponding to
                    # the bottom half.
                    old_type, old_lim = self.m_typ_tab[low_idx]
                    self.m_typ_tab.insert(low_idx, (old_type, low_lim))

                    if old_lim != hi_lim:
                        # The high limit does not reach the end of the old region. Insert a new
                        # entry for the new region's high limit.
                        self.m_typ_tab.insert(low_idx+1, (mem_type, hi_lim))
                    else:
                        # Change the type of the old node.
                        self.m_typ_tab[low_idx+1] = (mem_type, hi_lim)

                    popo.health |= HealthBit.CARD_TYPE_MEMORY
                    return self.send_popo(popo)
                else:
                    # Push back the end of the first category.
                    self.m_typ_tab[low_idx] = (self.m_typ_tab[low_idx][0], low_lim)

            if mem_type == self.m_typ_tab[low_idx][0]:
                # The new category matches the type of the first category. Extend out its end.
                self.m_typ_tab[low_idx] = (mem_type, hi_lim)

            elif self.m_typ_tab[hi_idx][0] != mem_type:
                # Insert a new category.
                self.m_typ_tab.insert(hi_idx, (mem_type, hi_lim))

        except BadMemory as e:
            popo.health |= e.args[0]

        popo.health |= HealthBit.CARD_TYPE_MEMORY
        return self.send_popo(popo)

    # Minor subroutines to shift two or three words right by one character.
    def _3srt_1c(self, afield):
        return ' ' + afield[:-1]

    def _2srt_1c(self, afield):
        return ' ' + afield[:15] + afield[16:]

    # Subroutine to break an address field down into subfields. Results are delivered in self._fieldcod[0:2],
    # and returned as adr_wd[0:2], as follows....
    #  _field_cod[0] all zero                Blank address field
    #  _field_cod[0] None                    Illegal format
    #  _field_cod[1] all zero                No modifier
    #  _field_cod[1] indicates signed num    Modifier given in adr_wd[1]
    #  _field_cod[0] indicates symbolic      Address symbol in adr_wd[0]
    #  _field_cod[0] indicates S or US num   Value given in adr_wd[0]
    def adr_field(self, popo):
        adr_wd = [None, None]

        if popo.address_1().isspace() and popo.address_2().isspace():
            # Indicate blank address field and exit.
            self._field_cod[0] = 0
            return adr_wd

        afield = popo.address_1() + popo.address_2() + ' '*8

        # Initially assume no modifier.
        self._field_cod[1] = 0

        # Set up to look for signs initially.
        also_main = None
        # Maximum number of NBCs in a subfield.
        max_nbcs = 8

        while max_nbcs > 0:
            # Branch when 2 words are right-justified.
            while afield[15] == ' ':
                afield = self._2srt_1c(afield)

            max_nbcs -= 1
            afield = self._3srt_1c(afield)

            # Branch if seeking sign and sign not preceded by a blank
            if also_main is None and afield[16] in '+-' and afield[15] == ' ':
                # Analyze possible modifier
                _, value = self.anal_subf(afield[16:], popo, check_blank=False)

                # Branch if twasn't a signed numeric subf.
                if (self._field_cod[0] & (FieldCodBit.NUMERIC | FieldCodBit.UNSIGNED)) != FieldCodBit.NUMERIC:
                    break

                # Branch if compound address.
                if afield[:16].isspace():
                    # Exit for signed numeric field.
                    adr_wd[0] = value
                    return adr_wd

                # Indicate presence of modifier.
                self._field_cod[1] = self._field_cod[0]
                # Save original form of rest of field.
                also_main = afield[:16] + ' '*8
                # Deliver value of modifier
                adr_wd[1] = value

                max_nbcs = 8
                afield = afield[:16] + ' '*8
                continue

            # Branch if more NBCs to examine.
            if afield[:16].isspace():
                # Analyze possible main address.
                _, value = self.anal_subf(afield[16:], popo, check_blank=False)

                # Branch if not numeric.
                if not self._field_cod[0] & FieldCodBit.NUMERIC:
                    break

                # Exit when main address is S or US num.
                adr_wd[0] = value
                return adr_wd
            else:
                # Seek another non-blank character.
                if max_nbcs == 0:
                    self._field_cod[0] = None
                    return adr_wd

        if also_main is None:
            # Set up putative symbolic subfield.
            afield = popo.address_1() + popo.address_2() + ' '*8
        else:
            # Recover non-modifier part of adr field.
            afield = also_main + ' '*8

        # Branch when possible head found.
        afield = self._3srt_1c(afield)
        while afield[16] == ' ':
            # Triple shift right to find head.
            afield = self._3srt_1c(afield)

        # Char preceded by non-blank isn't head.
        if afield[15] != ' ':
            # Backtrack after no-head finding.
            afield = afield[:8] + afield[9:16] + afield[8] + afield[16:]

            # Error if symbol is too long.
            if afield[15] != ' ' or not afield[:8].isspace():
                self._field_cod[0] = None
                return adr_wd

            # Finish backtracking.
            afield = afield[:15] + afield[16] + afield[16:]

            # Branch when symbol is normalized.
            while afield[8] == ' ':
                afield = afield[:8] + afield[9:16] + afield[8] + afield[16:]

            # Exit when main address is symbolic.
            adr_wd[0] = afield[8:16]
            return adr_wd

        if not afield[:8].isspace():
            # Move symbol right to insert head.
            while True:
                afield = self._2srt_1c(afield)

                # Error if no room for head.
                if afield[15] != ' ':
                    self._field_cod[0] = None
                    return adr_wd

                # Shift until normalized in afield[8:16].
                if afield[:8].isspace():
                    break

            # Insert head character.
            afield = afield[:15] + afield[16] + afield[16:]

            # Exit when main address is symbolic.
            adr_wd[0] = afield[8:16]
            return adr_wd

        # Exit when main address is 1-char sym.
        if afield[8:16].isspace():
            adr_wd[0] = afield[16:24]
            return adr_wd

        # Move symbol left to insert head.
        while True:
            if afield[8] != ' ':
                break
            afield = afield[:16] + afield[17:24] + afield[15] + afield[24:]

        # Insert head character.
        afield = afield[:15] + afield[16] + afield[16:]

        # Exit when main address is 1-char sym.
        adr_wd[0] = afield[8:16]
        return adr_wd

    def anal_subf(self, common, popo, check_blank=True):
        if check_blank and common.isspace():
            self._field_cod[0] = 0
            return common, None

        self._field_cod[0] = FieldCodBit.NUMERIC | FieldCodBit.POSITIVE | FieldCodBit.UNSIGNED
        while common[0] == ' ':
            common = common[1:] + common[0]

        subf = common
        dig_file = None

        if subf[0] != '0':
            if subf[0] in '+-':
                self._field_cod[0] &= ~FieldCodBit.UNSIGNED
                if subf[0] == '-':
                    self._field_cod[0] &= ~FieldCodBit.POSITIVE

                if subf[1:].isspace():
                    self._field_cod[0] = FieldCodBit.SYMBOLIC
                    return common, subf

                subf = subf[1:] + ' '

        decimal = False
        while subf[0] != ' ':
            if not subf[0].isnumeric():
                if (subf[0] != 'D'):
                    self._field_cod[0] = FieldCodBit.SYMBOLIC
                    return common, subf

                if not subf[1:].isspace():
                    self._field_cod[0] = FieldCodBit.SYMBOLIC
                    return common, subf

                if dig_file is None:
                    self._field_cod[0] = FieldCodBit.SYMBOLIC
                    return common, subf

                # Set up conversion, decimal to binary
                decimal = True
                break
            else:
                if subf[0] in '89':
                    # Telltale bits for 8s and 9s.
                    self._field_cod[0] |= FieldCodBit.DECIMAL

                if dig_file is None:
                    dig_file = '0'

                if dig_file != '0' or subf[0] != '0':
                    dig_file += subf[0]

            subf = subf[1:] + ' '

        # Set complaint when 8s or 9s and no D.
        if not decimal and self._field_cod[0] & FieldCodBit.DECIMAL:
            popo.health |= Bit.BIT9
            decimal = True

        if decimal:
            value = int(dig_file, 10)
        else:
            value = int(dig_file, 8)

        if not self._field_cod[0] & FieldCodBit.POSITIVE:
            value = -value

        return common, value

    def get_tape(self):
        if self._sypt is None:
            revno = self._yul.revno
            if not self._yul.switch & SwitchBit.REPRINT:
                revno -= 1
            self._sypt = self._yul.yulprogs.find_sypt(self._yul.comp_name, self._yul.prog_name, revno)
            if self._sypt is None:
                return None

        tape_card = self._sypt.readline()
        if tape_card == '':
            self._sypt.close()
            return None

        tape_card = tape_card[:80]

        tape = POPO(health=0, card=tape_card)

        # Clear asterisk if fetching main input, freezing subroutines, or not revising.
        cacn = SwitchBit.KNOW_SUBS | SwitchBit.FREEZE_P1 | SwitchBit.REVISION
        if (self._yul.switch & cacn) != (SwitchBit.KNOW_SUBS | SwitchBit.REVISION):
            if not self._yul.switch & SwitchBit.REPRINT: # FIXME
                tape.unmark()

        # Branch if no sequence break
        if tape.seq_break:
            # Set up post-break criterion.
            self._tape_cdno = Bit.BIT6
        else:
            card_no = tape.card[1:7]
            tape_card_no = int(card_no, 10)
            # Branch if sequence error.
            if tape_card_no <= (self._tape_cdno & 0xFFFFFFFFF):
                tape.health |= Bit.BIT7

            # Set up new criterion
            self._tape_cdno = tape_card_no

        return tape

    def head_tail(self, popo):
        if popo.health & HealthBit.ASTERISK:
            # Asterisk makes illegal op.
            return self.illeg(popo)

        self._head = popo.loc_field().strip()
        if self._head == '':
            self._head = ' '
        else:
            self._head = self._head[-1]

        # Store head in POPO.
        popo.health |= ALPHABET.index(self._head)
        popo.health |= HealthBit.CARD_TYPE_HEAD
        return self.send_popo(popo)

    def erase(self, popo):
        popo.health |= HealthBit.CARD_TYPE_ERASE

        if popo.health & HealthBit.ASTERISK:
            # Asterisk makes illegal op.
            return self.illegop(popo)

        # Decode address field.
        adr_wd = self.adr_field(popo)

        if self._field_cod[0] is None:
            # When address is meaningless.
            popo.health |= Bit.BIT11
            return self.er_loc_sym(popo)

        unsigned_mask = FieldCodBit.NUMERIC | FieldCodBit.UNSIGNED
        if (self._field_cod[0] & unsigned_mask) == unsigned_mask:
            # Lone numeric is both limits.
            if self._field_cod[1] == 0:
                adr_wd[1] = adr_wd[0]

            # Minus sign on modifier means thru.
            elif not self._field_cod[1] & FieldCodBit.POSITIVE:
                # Upper limit is negative of modifier.
                adr_wd[1] = -adr_wd[1]
                # Branch if limits are in OK order.
                if adr_wd[0] > adr_wd[1]:
                    # Bad news when lower limit is greater.
                    popo.health |= Bit.BIT12
                    return self.er_loc_sym(popo)
            else:
                # For plus modifier, upper limit is sum.
                adr_wd[0] += adr_wd[1]

            return self.ch_er_size(popo, adr_wd)

        elif self._field_cod[0] == FieldCodBit.SYMBOLIC:
            # Error if symbol is not ..ANYWHERE..
            if adr_wd[0] != 'ANYWHERE':
                popo.health |= Bit.BIT11
                return self.er_loc_sym(popo)

            # Mark card as leftover.
            popo.health |= Bit.BIT15
            if self._field_cod[1] == 0:
                # When symbol is alone.
                adr_wd[1] = 0
                return self.eras_lefto(popo, adr_wd)

            # Bad news when modifier is minus.
            if adr_wd[1] < 0:
                popo.health |= Bit.BIT11
                return self.er_loc_sym(popo)

            # Branch if modifier has OK size
            if adr_wd[1] <= 0o77777:
                return self.eras_lefto(popo, adr_wd)

            # When leftover block length too big.
            popo.health |= Bit.BIT12
            return self.er_loc_sym(popo)

        else:
            # Check for illegal loc cntr value.
            if self._loc_ctr >= ONES:
                popo.health |= Bit.BIT12
                return self.er_loc_sym(popo)

            # Branch if address field is not blank.
            if self._field_cod[0] == 0:
                # Erase current location only.
                adr_wd[1] = 0
            else:
                # Branch if theres 2 signed numeric parts.
                if self._field_cod[1] == 0:
                    adr_wd[1] = adr_wd[0]
                else:
                    adr_wd[1] = adr_wd[0] + adr_wd[1]

            # Area begins with loc cntr value anyhow.
            adr_wd[0] = self._loc_ctr

            # Negative upper limit means through here. Otherwise hi lim gave rel adres of end.
            if adr_wd[1] >= 0:
                adr_wd[1] += adr_wd[0]

            # Ensure positive upper limit.
            adr_wd[1] = abs(adr_wd[1])

            # Branch if limits are in OK order.
            if (adr_wd[0] > adr_wd[1]) or (adr_wd[1] >= self.adr_limit):
                popo.health |= Bit.BIT12
                return self.er_loc_sym(popo, adr_wd[0])

            # For blank or signed num addresses only.
            self._loc_ctr = adr_wd[1] + 1

            return self.ch_er_size(popo, adr_wd)

    def ch_er_size(self, popo, adr_wd):
        low_lim = adr_wd[0]
        hi_lim = adr_wd[1]

        # When address size(s) are wrong.
        if hi_lim > self.max_loc or low_lim >= ONES:
            popo.health |= Bit.BIT12
            return self.er_loc_sym(popo, low_lim)

        # Put limits into card.
        popo.health |= (low_lim << 16) | hi_lim

        # Look up memory type of lower limit.
        midx = 0
        while low_lim > self.m_typ_tab[midx][1]:
            midx += 1
        mem_type = self.m_typ_tab[midx][0]

        # Error if lower not erasable.
        if mem_type != MemType.ERASABLE or hi_lim > self.m_typ_tab[midx][1]:
            popo.health |= Bit.BIT13
            return self.er_loc_sym(popo, low_lim)

        # Check availability of block.
        loc_loc = low_lim
        while loc_loc <= hi_lim:
            if not self.avail(loc_loc, reserve=True):
                # Signal conflict.
                popo.health |= Bit.BIT14
            loc_loc += 1

        return self.er_loc_sym(popo, low_lim)

    def er_loc_sym(self, popo, low_lim=0):
        # Analyze location field of non-leftover.
        common, value = self.anal_subf(popo.loc_field(), popo)
        if self._field_cod[0] == 0:
            # OK exit if blank.
            return self.send_popo(popo)

        unsigned_mask = FieldCodBit.NUMERIC | FieldCodBit.UNSIGNED
        if (self._field_cod[0] & unsigned_mask) == unsigned_mask:
            # Error exit if unsigned numeric.
            popo.health |= Bit.BIT16
            return self.send_popo(popo)
        elif self._field_cod[0] != FieldCodBit.SYMBOLIC:
            # OK exit if signed numeric.
            return self.send_popo(popo)

        # Analyze location symbol.
        popo.health |= Bit.BIT8
        sym_name = common.strip()
        symbol = self.anal_symb(sym_name)

        # Error exit if symbol table is full.
        if symbol is None:
            popo.health |= Bit.BIT16
            return self.send_popo(popo)

        # Get address of location transforms.
        sym_xform = self._xforms[symbol.health]

        # Symbol health becomes F if illeg. adr.
        if popo.health & Bit.BIT11:
            new_health = 0xF
            return self.end_is(popo, 0, symbol, new_health)

        # Select and apply transform for erase location symbol.
        if popo.health & Bit.BIT12:
            # Use transform for oversize assignment.
            new_health = (sym_xform >> 7*4) & 0xF
            return self.end_is(popo, 0, symbol, new_health)

        if popo.health & Bit.BIT13:
            # Use transform for oversize assignment.
            new_health = (sym_xform >> 6*4) & 0xF
            return self.end_is(popo, low_lim, symbol, new_health)

        if popo.health & Bit.BIT14:
            # Use transform for conflict.
            new_health = (sym_xform >> 5*4) & 0xF
            return self.end_is(popo, low_lim, symbol, new_health)

        # Use normal erase transform.
        new_health = (sym_xform >> 8*4) & 0xF
        return self.end_is(popo, low_lim, symbol, new_health)

    def eras_lefto(self, popo, adr_wd):
        # FIXME: implement leftovers
        pass

    def octal(self, popo):
        popo.health |= HealthBit.CARD_TYPE_OCTAL
        return self.inst_dec_oct(popo)

    def instruct(self, popo):
        popo.health |= HealthBit.CARD_TYPE_INSTR
        return self.inst_dec_oct(popo)

    def decimal(self, popo):
        popo.health |= HealthBit.CARD_TYPE_DECML
        return self.inst_dec_oct(popo)

    def _2octal(self, popo):
        popo.health |= HealthBit.CARD_TYPE_2OCTAL
        return self._2oct_2dec(popo)

    def _2decimal(self, popo):
        popo.health |= HealthBit.CARD_TYPE_2DECML
        return self._2oct_2dec(popo)

    def _2oct_2dec(self, popo):
        # Set up later test
        self._save_loc = ONES

        self._yul.switch &= ~MemType.MEM_MASK
        self._yul.switch |= MemType.FIXED

        if popo.card[0] == 'J':
            # FIXME: Implement leftovers!
            pass
        else:
            # Translate regular location field.
            self._loc_state = 0
            self.location(popo)

        popo.health |= self._loc_state
        if popo.health & (Bit.BIT12 | Bit.BIT14) != 0:
            # Exit if leftover or oversize location.
            return self.send_popo(popo)

        # Branch if loc ctr was not saved.
        if self._save_loc < ONES:
            self._loc_ctr = (popo.health & 0xFFFF) + 1

        loc_value = self._loc_ctr
        # Branch if size of 2nd loc is OK.
        if not self.incr_lctr() or loc_value > self.max_loc:
            popo.health |= Bit.BIT14
            self._loc_ctr = ONES
            return self.dp_loc_end(popo)

        # Find memory type (this happened in LOCATION, but wasn't saved in this port)
        midx = 0
        while loc_value > self.m_typ_tab[midx][1]:
            midx += 1

        # Branch if 1st loc in bad memory type or end of category.
        if (popo.health & Bit.BIT15) or (popo.health & 0xFFFF == self.m_typ_tab[midx][1]):
            # Which would mean type error on at least one of the locations.
            popo.health |= Bit.BIT15

            if popo.health & HealthBit.SYMBOLIC:
                # If loc is symbolic and in table, use the DP type error transformation.
                sym_xform = 0xFEECEE9EC900FEEC
                symbol = self.anal_symb(popo.loc_field().strip())
                symbol.health = (sym_xform >> (symbol.health*4)) & 0xF

            return self.dp_loc_end(popo)

        # Test and reserve 2nd location. Branch if it was available.
        if not self.avail(loc_value, reserve=True):
            popo.health |= Bit.BIT16

            # With same conditions as for type error, use DP conflict transform.
            if popo.health & HealthBit.SYMBOLIC:
                sym_xform = 0xFEDEEAEEDA00FEDE
                symbol = self.anal_symb(popo.loc_field().strip())
                symbol.health = (sym_xform >> (symbol.health*4)) & 0xF

        return self.dp_loc_end(popo)

    def dp_loc_end(self, popo):
        if self._save_loc < ONES:
            # Restore loc ctr and exit.
            self._loc_ctr = self._save_loc
        return self.send_popo(popo)

    def even(self, popo):
        if popo.health & HealthBit.ASTERISK:
            # Asterisk makes illegal op.
            return self.illegop(popo)

        if not popo.address_1().isspace() or not popo.address_2().isspace():
            # Cuss mildly at non-blank address fields.
            popo.health |= Bit.BIT13

        if self._loc_ctr >= self.max_loc:
            # Cuss attempt to fly off the end.
            popo.health |= Bit.BIT14
        elif self._loc_ctr & 1:
            # Location is odd, so add one.
            self._loc_ctr += 1

        popo.health |= HealthBit.CARD_TYPE_EVEN
        return self.ch_il_size(popo, self._loc_ctr, [None, None])


    def is_equals(self, popo):
        popo.health |= HealthBit.CARD_TYPE_EQUALS
        return self.decod_adr(popo, 0)

    def equ_minus(self, popo):
        popo.health |= HealthBit.CARD_TYPE_EQUALS
        return self.decod_adr(popo, self._loc_ctr)

    def equ_plus(self, popo):
        popo.health |= HealthBit.CARD_TYPE_EQUALS
        return self.decod_adr(popo, -self._loc_ctr)

    def setloc(self, popo):
        popo.health |= HealthBit.CARD_TYPE_SETLOC
        return self.decod_adr(popo, 0)

    def decod_adr(self, popo, loc_loc):
        # Asterisk makes illegal op.
        if popo.health & HealthBit.ASTERISK:
            return self.illegop(popo)

        # Decode address field.
        adr_wd = self.adr_field(popo)

        # Abort if meaningless address field.
        if self._field_cod[0] is None:
            popo.health |= HealthBit.MEANINGLESS
            return self.no_adress(popo, adr_wd)

        # Bad loc ctr kills =PLUS and =MINUS now.
        if loc_loc >= ONES:
            return self.ch_il_size(popo, loc_loc, adr_wd, check_loc=False)

        # If blank adr field, fake up absolute.
        if self._field_cod[0] == 0:
            self._field_cod[0] = FieldCodBit.NUMERIC | FieldCodBit.UNSIGNED
            if self._loc_ctr >= ONES:
                return self.ch_il_size(popo, loc_loc, adr_wd, check_loc=False)
            adr_wd[0] = self._loc_ctr
            self._field_cod[1] = 0

        if self._field_cod[1] == 0:
            # Fake up a modifier if it lacks one.
            self._field_cod[1] = FieldCodBit.NUMERIC
            adr_wd[1] = loc_loc
        else:
            # Combine loc ctr with exisiting modifier.
            adr_wd[1] += loc_loc

        # Set up sign of net modifier.
        if adr_wd[1] > 0:
            self._field_cod[1] |= FieldCodBit.POSITIVE
        else:
            self._field_cod[1] &= ~FieldCodBit.POSITIVE

        unsigned_mask = FieldCodBit.NUMERIC | FieldCodBit.UNSIGNED
        if (self._field_cod[0] & unsigned_mask) == unsigned_mask:
            # Branch if main part is unsigned numeric.
            pass
        elif self._field_cod[0] == FieldCodBit.SYMBOLIC:
            # Branch if address field contains a sym.
            return self.sym_is_loc(popo, loc_loc, adr_wd)
        elif self._loc_ctr >= ONES:
            # Branch if location counter is bad.
            return self.ch_il_size(popo, loc_loc, adr_wd, check_loc=False)
        else:
            # Form address relative to L.C. setting.
            adr_wd[0] += self._loc_ctr

        # Add modifier part to unsigned numeric.
        adr_wd[0] += adr_wd[1]
        # Go to test size of num + modifier.
        loc_loc = adr_wd[0]
        return self.ch_il_size(popo, loc_loc, adr_wd)

    def sym_is_loc(self, popo, loc_loc, adr_wd):
        # Analyze address symbol history.
        sym_name = adr_wd[0].strip()
        symbol = self.anal_symb(sym_name)

        # Exit if symbol table is full.
        if symbol is None:
            popo.health |= Bit.BIT16
            return self.no_adress(popo, adr_wd, symbol)

        # Store address of address symbol.
        popo.health |= (symbol.index + 1) << 16

        if symbol.health > 0x0 and symbol.health < 0x3:
            # Signal address nearly defined.
            popo.health |= HealthBit.NEARLY_DEFINED
            return self.no_adress(popo, adr_wd, symbol)

        # Use health of symbol to find transform.
        sym_xform = self._xforms[symbol.health]

        # Test predefinition bit.
        if not sym_xform & 0x1000000000:
            # Signal address undefined as yet.
            popo.health |= HealthBit.UNDEFINED
            return self.no_adress(popo, adr_wd, symbol)

        # Test def/no-def bit.
        if not sym_xform & 0x2000000000:
            popo.health |= HealthBit.ILL_DEFINED
            return self.no_adress(popo, adr_wd, symbol)

        # Add modifier to symbol definition.
        loc_loc = symbol.value
        loc_loc += adr_wd[1]

        return self.ch_il_size(popo, loc_loc, adr_wd, symbol)

    def ch_il_size(self, popo, loc_loc, adr_wd, adr_symbol=None, check_loc=True):
        if not check_loc or loc_loc >= ONES:
            popo.health |= HealthBit.OVERSIZE
            return self.no_adress(popo, adr_wd, adr_symbol)

        popo.health |= loc_loc & 0xFFFF

        # Branch for normal IS,= path.
        if (popo.health & HealthBit.CARD_TYPE_MASK) == HealthBit.CARD_TYPE_EQUALS:
            return self.iseq_lsym(popo, loc_loc, adr_wd, adr_symbol)

        # Look up memory type for setloc.
        midx = 0
        while loc_loc > self.m_typ_tab[midx][1]:
            midx += 1
        mem_type = self.m_typ_tab[midx][0]

        if mem_type == MemType.SPEC_NON:
            # Signal setloc to spec/non memory.
            popo.health |= Bit.BIT10
        else:
            self._loc_ctr = popo.health & 0xFFFF

        return self.nd_setloc(popo)

    def nd_setloc(self, popo):
        if not popo.loc_field().isspace():
            # Cuss about non-blank loc field in loc.
            popo.health |= HealthBit.SYMBOLIC

        return self.send_popo(popo)

    def iseq_lsym(self, popo, loc_loc, adr_wd, adr_symbol=None):
        common, value = self.anal_subf(popo.loc_field(), popo)
        if self._field_cod[0] != FieldCodBit.SYMBOLIC:
            return self.send_popo(popo)

        # Signal symb locn, get symbol history.
        popo.health |= HealthBit.SYMBOLIC
        sym_name = common.strip()
        symbol = self.anal_symb(sym_name)

        # Abort if symbol table is full.
        if symbol is None:
            popo.health |= Bit.BIT15
            return self.send_popo(popo)

        # Save symbol, get address of transform.
        sym_xform = self._xforms[symbol.health]
        if symbol.health <= 2 or symbol.heatlh != 5:
            # Branch if loc sym was not leftover.
            return self.it_is(popo, loc_loc, symbol, sym_xform, adr_wd, adr_symbol, check_loc=True)

        # Branch if an OK definition was made.
        if loc_loc >= ONES:
            # Throw up hands if EQUALS failed to def.
            new_health = 0xF
            return self.not_ok_def(popo, loc_loc, symbol, sym_xform, adr_wd, adr_symbol)

        if symbol.value < 0:
            # When symbol goes with leftover erase.
            sym_type = MemType.ERASABLE
        else:
            # When symbol goes with lefto con or inst.
            sym_type = MemType.FIXED

        # Branch when memory type is known.
        midx = 0
        while loc_loc > self.m_typ_tab[midx][1]:
            midx += 1
        mem_type = self.m_typ_tab[midx][0]

        # Br if leftover equated to wrong type.
        if sym_type != mem_type:
            # Indicate type error in symbol table.
            new_health = 0xC
            return self.end_is(popo, loc_loc, symbol, new_health)

        hi_lim = loc_loc + abs(sym.value)
        if hi_lim > self._m_typ_tab[midx][1]:
            new_health = 0xC
            return self.end_is(popo, loc_loc, symbol, new_health)

        for loc in range(loc_loc, hi_lim):
            if not self.avail(loc, reserve=True):
                # Force special transform if conflict
                sym_xform = 0xA000

        adr_wd[1] = hi_lim

        return self.it_is(popo, loc_loc, symbol, sym_xform, adr_wd, adr_symbol)


    def it_is(self, popo, loc_loc, symbol, sym_xform, adr_wd, adr_symbol=None, check_loc=False):
        if check_loc and loc_loc >= ONES:
            return self.not_ok_def(popo, loc_loc, symbol, sym_xform, adr_wd, adr_symbol)

        new_health = (sym_xform >> 3*4) & 0xF
        return self.end_is(popo, loc_loc, symbol, new_health)

    def end_is(self, popo, loc_loc, symbol, new_health):
        self._loc_state = LocStateBit.SYMBOLIC
        self.sy_def_xit(loc_loc, symbol, new_health)

        # Exit unless loc symbol failed to fit.
        b8b17 = Bit.BIT8 | Bit.BIT17
        if (self._loc_state & b8b17) != b8b17:
            return self.send_popo(popo)

        # Branch if op code is equals.
        if popo.health & HealthBit.CARD_TYPE_EQUALS:
            # Show unfitting of equals loc sym.
            popo.health |= Bit.BIT15
        else:
            # Show unfitting of erase loc sym.
            popo.health |= Bit.BIT15

        return self.send_popo(popo)

    def not_ok_def(self, popo, loc_loc, symbol, sym_xform, adr_wd, adr_symbol=None):
        if popo.health & Bit.BIT13:
            new_health = 0xF
            return self.end_is(popo, loc_loc, symbol, new_health)

        if popo.health & Bit.BIT14:
            new_health = (sym_xform >> 1*4) & 0xF
            return self.end_is(popo, loc_loc, symbol, new_health)

        if abs(adr_wd[1]) > 0o77777:
            popo.health |= HealthBit.OVERSIZE
            new_health = (sym_xform >> 1*4) & 0xF
            return self.end_is(popo, loc_loc, symbol, new_health)

        symbol.definer = adr_symbol.name
        if symbol.name not in adr_symbol.definees:
            adr_symbol.definees.append(symbol.name)

        new_health = (sym_xform >> 2*4) & 0xF
        return self.end_is(popo, adr_wd[1], symbol, new_health)

    def no_adress(self, popo, adr_wd, adr_symbol=None):
        if (popo.health & HealthBit.CARD_TYPE_MASK) != HealthBit.CARD_TYPE_EQUALS:
            return self.nd_setloc(popo)

        loc_loc = ONES
        return self.iseq_lsym(popo, loc_loc, adr_wd, adr_symbol)

    def block(self, popo):
        # Asterisk makes illegal op.
        if popo.health & HealthBit.ASTERISK:
            return self.illegop(popo)

        # Decode address field.
        adr_wd = self.adr_field(popo)
        if self._field_cod[0] is None or self._field_cod[0] & FieldCodBit.SYMBOLIC:
            # When address field is meaningless or there is no numeric part.
            return self.ilfo_blok(popo)

        # Branch if address field is blank or main part is signed num.
        unsigned_mask = FieldCodBit.NUMERIC | FieldCodBit.UNSIGNED
        if (self._field_cod[0] & unsigned_mask) != unsigned_mask:
            if self._field_cod[0] != 0:
                if self._field_cod[1] == 0:
                    adr_wd[1] = adr_wd[0]
                else:
                    adr_wd[1] += adr_wd[0]

            if self._loc_ctr >= ONES:
                # Cannot evaluate rel to bad location.
                popo.health |= Bit.BIT14
                return self.block_loc(popo)

            # Set loc value to beginning of bank.
            loc_value = self._loc_ctr & ~self.blok_ones

            # Show whether modifier is present
            self._field_cod[1] = self._field_cod[0]

        else:
            # Shift amount supplied by initialization.
            loc_value = adr_wd[0] << self.blok_shif
            # Omit increase for blank bank.
            if self._field_cod[0] != 0:
                loc_value += (self.bank_inc << self.blok_shif)

        # Branch if there is no modifier.
        if self._field_cod[1] != 0:
            # Error if modifier is minus or modifier greater than block size.
            if adr_wd[1] < 0 or adr_wd[1] > self.blok_ones:
                return self.ilfo_blok(popo)

            # Add modifier to shifted numeric.
            loc_value += adr_wd[1]

        if loc_value > self.max_loc:
            # Exit for no such block.
            popo.health |= Bit.BIT11
            return self.block_loc(popo)

        # Look up memory type.
        midx = 0
        while loc_value > self.m_typ_tab[midx][1]:
            midx += 1
        mem_type = self.m_typ_tab[midx][0]

        # Branch if in fixed or erasable.
        if mem_type == MemType.SPEC_NON:
            # Memory type error exit.
            popo.health |= Bit.BIT13
            return self.block_loc(popo)

        loc = loc_value
        # Form end of major block.
        loc_value |= self.blok_ones

        # Branch if major block end comes first.
        if loc_value > self.m_typ_tab[midx][1]:
            # When minor block end comes first.
            loc_value = self.m_typ_tab[midx][1]

        # Non-destructive availability test.
        while loc <= loc_value:
            # Branch if available.
            if self.avail(loc, reserve=False):
                # Store found address.
                popo.health |= loc
                # Set loc ctr accordingly.
                self._loc_ctr = loc
                return self.block_loc(popo)

            loc += 1

        # When block is full.
        popo.health |= Bit.BIT10
        return self.block_loc(popo)

    def ilfo_blok(self, popo):
        popo.health |= Bit.BIT12
        return self.block_loc(popo)

    def block_loc(self, popo):
        if not popo.loc_field().isspace():
            popo.health |= Bit.BIT8
        popo.health |= HealthBit.CARD_TYPE_BLOCK
        return self.send_popo(popo)

    def subro(self, popo):
        pass

    def count(self, popo):
        pass

    def late_mem(self, popo):
        popo.health |= HealthBit.CARD_TYPE_2LATE
        return self.send_popo(popo)

def inish_p1(mon, yul):
    # Move freeze indicator to bit 8, B17=0
    if yul.switch & SwitchBit.FREEZE:
        yul.switch &= ~SwitchBit.FREEZE
        yul.switch |= SwitchBit.FREEZE_P1

    comp_pass1 = mon.phi_load(yul.comp_name + '.PASS1', yul)
    if comp_pass1 is None:
        yul.typ_abort()

    comp_pass1.m_special()

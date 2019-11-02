import importlib
from yul_system.types import Bit, SwitchBit, FieldCodBit, HealthBit, MemType

class POPO:
    def __init__(self, health=0, card=''):
        self.health = health
        self.card = card

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

class Pass1:
    def __init__(self, mon, yul):
        self._mon = mon
        self._yul = yul
        self._real_cdno = 0
        self._field_cod = [None, None]
        self._end_of = POPO(health=0, card='⌑999999Q' + 72*' ')
        self._early = True
        self._op_found = None
        self._test_done = False

    def post_spec(self):
        while not self._test_done:
            self.get_real()
            self.process(self._real, self._real_cdno)

    def get_real(self):
        # Get real is normally the chief node of pass 1. Occasionally merge control procedures take
        # over, accepting or rejecting tape cards.

        # Get a card and branch on no end of file.
        card = self.get_card()
        if card is None:
            # Run out tape cards at end of file.
            self._test_done = True

        if self._yul.switch & SwitchBit.MERGE_MODE:
            if not self._yul.switch & SwitchBit.TAPE_KEPT:
                self._tape = self.get_tape()

                if self._tape is None:
                    # FIXME: Clean up and exit pass 1
                    return

        self.modif_chk()

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

        # Clear zone bits of vertical format.
        vertical_format = ord(self._real.card[7]) & 0xF

        # Mark all cards entering during merging.
        if self._yul.switch & SwitchBit.MERGE_MODE:
            vertical_format |= 0x10

        self._real.card = self._real.card[:7] + chr(vertical_format) + self._real.card[8:]

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
                # Remove confusing info from log card.
                self._real.card = self._real.card[0] + '      ' + self._real.card[7:]
                seq_break = True


            # Branch if not TINS (Tuck In New Section)... which is an incipient log card.
            if self._real.card[0] == 'L':
                seq_break = True

            # Op code "MODIFY" is automatic seq. brk.
            if self._real.card[0] == ' ' and self._real.card[16:22] == 'MODIFY':
                seq_break = True

        if seq_break:
            # Insert sequence break bit in card.
            vertical_format |= 0x20
            self._real.card = self._real.card[:7] + chr(vertical_format) + self._real.card[8:]

            # Set up criterion after sequence break.
            self._real_cdno = Bit.BIT6
            return self._real.card

        real_card_no = int(card_no, 10)

        if real_card_no <= self._real_cdno:
            # Disorder
            self._real.health |= Bit.BIT7

        # Keep normal form of card number on tape.
        self._real.card = self._real.card[0] + card_no + self._real.card[7:]

        self.real_cdno = real_card_no
        return self._real.card

    def send_popo(self, popo):
        # FIXME: Renumber and append POPO
        print('%016o:%s' % (popo.health, popo.card))

    def modif_chk(self):
        pass

    def proc_real(self):
        return process(self._real, self._real_cdno)

    def proc_tape(self):
        return process(self._tape, self._tape_cdno)

    def process(self, popo, cdno):
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
            # Branch if dashes should be put in date.
            if popo.card[67:69] != '  ' or popo.card[70:72] != '  ':
                popo.card = popo.card[:69] + '-' + popo.card[70:72] + '-' + popo.card[73:]

            # FIXME: Send a dummy acceptor ahead of a marked log card entering as a member of a called subro
            popo.health |= HealthBit.CARD_TYPE_REMARK
            return self.send_popo(popo)

        op_field = popo.op_field()[1:7]

        if self._early:
            if op_field == 'MEMORY':
                return self.memory(popo)

            if op_field == 'SEGNUM':
                return self.segnum(popo)

            self._early = False

        common, value = self.anal_subf(op_field)
        operation = common.strip()

        try:
            if self._field_cod[0] is None:
                raise IllegalOp()

            elif self._field_cod[0] in (0, FieldCodBit.SYMBOLIC):
                if operation != '' and operation[-1] == '*':
                    popo.health |= Bit.BIT11
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
            self._yul.switch &= ~(Bit.BIT25 | Bit.BIT26 | Bit.BIT27)
            self._yul.switch |= MemType.FIXED
            self._loc_state = 0
            # FIXME: BLNK LOCN
            popo.health |= HealthBit.CARD_TYPE_ILLOP
            return self.reg_incon(popo, translate_loc=False)

        self._yul.switch &= ~(MemType.ERASABLE | MemType.SPEC_NON)
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

            if hi_lim > self.adr_limit:
                raise BadMemory(Bit.BIT12)

            popo.health |= hi_lim & 0xFFFF

            common, value = self.anal_subf(popo.loc_field())
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
                _, value = self.anal_subf(afield[16:])

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
                _, value = self.anal_subf(afield[16:])

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

    def anal_subf(self, common, check_blank=False):
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
                self._field_cod[0] |= FieldCodBit.DECIMAL
                break
            else:
                if subf[0] in '89':
                    self._field_cod[0] |= FieldCodBit.DECIMAL

                if dig_file is None:
                    dig_file = '0'

                if dig_file != '0' or subf[0] != '0':
                    dig_file += subf[0]

            subf = subf[1:] + ' '

        if self._field_cod[0] & FieldCodBit.DECIMAL:
            value = int(dig_file, 10)
        else:
            value = int(dig_file, 8)

        if not self._field_cod[0] & FieldCodBit.POSITIVE:
            value = -value

        return common, value

    def get_tape(self):
        # FIXME: Read from SYPT and SYLT
        return None

    def head_tail(self, popo):
        pass

    def is_equals(self, popo):
        pass

    def erase(self, popo):
        pass

    def octal(self, popo):
        pass

    def decimal(self, popo):
        pass

    def _2octal(self, popo):
        pass

    def _2decimal(self, popo):
        pass

    def even(self, popo):
        pass

    def setloc(self, popo):
        pass

    def subro(self, popo):
        pass

    def equ_plus(self, popo):
        pass

    def equ_minus(self, popo):
        pass

    def count(self, popo):
        pass

    def late_mem(self, popo):
        pass

def inish_p1(mon, yul):
    try:
        comp_mod = importlib.import_module('yul_system.assembler.' + yul.comp_name.lower() + '.pass_1')
        comp_pass1_class = getattr(comp_mod, yul.comp_name + 'Pass1')
        comp_pass1 = comp_pass1_class(mon, yul)
    except:
        mon.mon_typer('UNABLE TO LOAD PASS 1 FOR COMPUTER %s' % yul.comp_name)
        yul.typ_abort()

    comp_pass1.m_special()

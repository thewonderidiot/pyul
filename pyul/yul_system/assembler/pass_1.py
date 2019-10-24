import importlib
from yul_system.assembler.pass_0 import Bit, SwitchBit

class HealthBit:
    CARD_TYPE_MASK   = Bit.BIT1 | Bit.BIT2 | Bit.BIT3 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6
    CARD_TYPE_END_OF =        0 |        0 |        0 |        0 |        0 |        0 # 00
    CARD_TYPE_MODIFY =        0 |        0 |        0 |        0 |          | Bit.BIT6 # 01
    CARD_TYPE_CARDNO =        0 |        0 |        0 |        0 | Bit.BIT5 | Bit.BIT6 # 03
    CARD_TYPE_ACCEPT =        0 |        0 |        0 | Bit.BIT4 |        0 |        0 # 04
    CARD_TYPE_DELETE =        0 |        0 |        0 | Bit.BIT4 |          | Bit.BIT6 # 05
    CARD_TYPE_REMARK =        0 |        0 |        0 | Bit.BIT4 | Bit.BIT5 |        0 # 06
    CARD_TYPE_RIGHTP =        0 |        0 |        0 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6 # 07
    CARD_TYPE_ALIREM =        0 |        0 | Bit.BIT3 |        0 |        0 |        0 # 10
    CARD_TYPE_MEMORY =        0 |        0 | Bit.BIT3 |        0 |        0 | Bit.BIT6 # 11
    CARD_TYPE_INSTR  =        0 |        0 | Bit.BIT3 |        0 | Bit.BIT5 |        0 # 12
    CARD_TYPE_ILLOP  =        0 |        0 | Bit.BIT3 |        0 | Bit.BIT5 | Bit.BIT6 # 13
    CARD_TYPE_DECML  =        0 |        0 | Bit.BIT3 | Bit.BIT4 |        0 |        0 # 14
    CARD_TYPE_OCTAL  =        0 |        0 | Bit.BIT3 | Bit.BIT4 |        0 | Bit.BIT6 # 15
    CARD_TYPE_EQUALS =        0 |        0 | Bit.BIT3 | Bit.BIT4 | Bit.BIT5 |        0 # 16
    CARD_TYPE_SETLOC =        0 |        0 | Bit.BIT3 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6 # 17
    CARD_TYPE_ERASE  =        0 | Bit.BIT2 |        0 |        0 |        0 |        0 # 20
    CARD_TYPE_2CTAL  =        0 | Bit.BIT2 |        0 |        0 |        0 | Bit.BIT6 # 21
    CARD_TYPE_2DECML =        0 | Bit.BIT2 |        0 |        0 | Bit.BIT5 |        0 # 22
    CARD_TYPE_BLOCK  =        0 | Bit.BIT2 |        0 |        0 | Bit.BIT5 | Bit.BIT6 # 23
    CARD_TYPE_HEAD   =        0 | Bit.BIT2 |        0 | Bit.BIT4 |        0 |        0 # 24
    CARD_TYPE_2LATE  =        0 | Bit.BIT2 |        0 | Bit.BIT4 |        0 | Bit.BIT6 # 25
    CARD_TYPE_SUBRO  =        0 | Bit.BIT2 |        0 | Bit.BIT4 | Bit.BIT5 |        0 # 26
    CARD_TYPE_NWINST =        0 | Bit.BIT2 |        0 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6 # 27
    CARD_TYPE_EVEN   =        0 | Bit.BIT2 | Bit.BIT3 |        0 |        0 |        0 # 30
    CARD_TYPE_COUNT  =        0 | Bit.BIT2 | Bit.BIT3 |        0 |        0 | Bit.BIT6 # 31
    CARD_TYPE_SEGNUM =        0 | Bit.BIT2 | Bit.BIT3 |        0 | Bit.BIT5 |        0 # 32

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

class Pass1:
    def __init__(self, mon, yul):
        self._mon = mon
        self._yul = yul
        self._real_cdno = 0
        self._end_of = POPO(health=0, card='⌑999999Q' + 72*' ')

    def post_spec(self):
        while True:
            self.get_real()

    def get_real(self):
        # Get real is normally the chief node of pass 1. Occasionally merge control procedures take
        # over, accepting or rejecting tape cards.

        # Get a card and branch on no end of file.
        card = self.get_card()
        if card is None:
            # Run out tape cards at end of file.
            pass

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
        if self._yul.switch & SwitchBit.MERGING:
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
            is card_no == 'SEQBRK':
                seq_break = True

            # Allow for "LOG" in col 2-7 of acceptor.
            else if self._real.card[0] == '=':
                seq_break = True

            # Show illegal number field by zero.
            else:
                card_no = '000000'

        # Card number 999999 is a sequence break.
        if card_no = '999999':
            seq_break = True

        # Do not test column 1 of right print.
        if self._real.card[7] != '9':
            # A log card is an automatic sequence break.
            if self._real.card[0] == 'L':
                # Remove confusing info from log card.
                self._real.card = self._real.card[0] + '      ' + self._real.card[8:]
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

        card_no = int(card_no, 10)

        if card_no <= self._real_cdno:
            # Disorder
            self._real.health |= Bit.BIT7

        # Keep normal form of card number on tape.
        self._real.card = self._real.card[0] + card_no + self._real.card[7:]

        self.real_cdno = card_no
        return self._real.card

    def get_tape(self):
        # FIXME: Read from SYPT and SYLT
        return None

    def head_tail(self):
        pass

    def is_equals(self):
        pass

    def erase(self):
        pass

    def octal(self):
        pass

    def decimal(self):
        pass

    def _2octal(self):
        pass

    def _2decimal(self):
        pass

    def even(self):
        pass

    def setloc(self):
        pass

    def subro(self):
        pass

    def equ_plus(self):
        pass

    def equ_minus(self):
        pass

    def count(self):
        pass

    def late_mem(self):
        pass

def inish_p1(mon, yul):
    try:
        comp_mod = importlib.import_module('yul_system.assembler.' + yul.comp_name.lower() + '.pass_1')
        comp_pass1_class = getattr(comp_mod, yul.comp_name + 'Pass1')
        comp_pass1 = comp_pass1_class(mon, yul)
        comp_pass1.m_special()
    except:
        mon.mon_typer('UNABLE TO LOAD PASS 1 FOR COMPUTER %s' % yul.comp_name)
        yul.typ_abort()

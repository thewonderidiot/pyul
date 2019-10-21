import importlib
from yul_system.assembler.pass_0 import Bit, SwitchBit

class Pass1:
    def __init__(self, mon, yul):
        self._mon = mon
        self._yul = yul
        self._real_cdno = 0

    def post_spec(self):
        while True:
            self.get_real()

    def get_real(self):
        card = self.get_card()
        if card is None:
            # Create "END OF" card
            pass
        else:
            pass

    def get_card(self):
        card = self._mon.mon_peek()
        if card[0] in 'Y*':
            if card[0] == 'Y':
                self.yul.switch |= SwitchBit.ANOTHER_TASK
            self._real_cdno = Bit.BIT6
            return None

        if self.yul.switch & SwitchBit.REPRINT:
            return None

        self._real_card = self._mon.mon_read()
        if self._real_card[7] == ' ':
            self._real_card = self._real_card[:7] + '1' + self._real_card[8:]
        elif self._real_card[7] == '-':
            self._real_card = self._real_card[:7] + '2' + self._real_card[8:]
        elif not self._real_card[7].isnumeric():
            self._real_card = self._real_card[:7] + '8' + self._real_card[8:]

        vertical_format = ord(self._real_card[7]) & 0xF
        if self.yul.switch & SwitchBit.MERGING:
            vertical_format |= 0x10
        self._real_card = self._real_card[:7] + chr(vertical_format) + self._real_card[8:]

        if not (self._real_card[0].isalnum() or self._real_card[0] in '=\' '):
            self._real_card = '■' + self._real_card[1:]

        self._rl_cd_hlth = 0

        card_no = self._real_card[1:7]
        card_no = card_no.replace(' ', '0')

        seq_break = False
        test_col1 = True

        if not card_no.isnumeric():
            is card_no == 'SEQBRK':
                seq_break = True
            else if self._real_card[0] == '=':
                seq_break = True
            else:
                card_no = '000000'
        else:
            if card_no = '999999':
                seq_break = True

            if self._real_card[7] == '9':
                test_col1 = False

        if not seq_break and test_col1:
            if (self._real_card[0] in 'LT') or (self._real_card[0] == ' ' and self._real_card[16:22] == 'MODIFY'):
                self._real_card = self._real_card[0] + '      ' + self._real_card[8:]
                seq_break = True

        if seq_break:
            vertical_format |= 0x20
            self._real_cdno = Bit.BIT6
            return self._real_card

        card_no = int(card_no, 10)

        if card_no <= self._real_cdno:
            self.rl_cd_hlth |= Bit.BIT7

        self.real_cdno = card_no
        return self._real_card

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

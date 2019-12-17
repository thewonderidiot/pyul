from yul_system.assembler.pass3 import Pass3
from yul_system.types import ONES

class Agc4Pass3(Pass3):
    def __init__(self, mon, yul, old_line, m_typ_tab, wd_recs):
        super().__init__(mon, yul, old_line, m_typ_tab, wd_recs)
        self._stick_nos = [
            ('B28', 'R1B'),
            ('B29', 'R2A'),
            ('B29', 'R2B'),
            ('B28', 'R1A'),
            ('B21', 'S1B'),
            ('B22', 'S2A'),
            ('B22', 'S2B'),
            ('B21', 'S1A'),
            ('B23', 'T1B'),
            ('B24', 'T2A'),
            ('B24', 'T2B'),
            ('B23', 'T1A'),
        ]

        self._wire_nos = [
            '1-16)   ',
            '17-32)  ',
            '33-48)  ',
            '49-64)  ',
            '65-80)  ',
            '81-96)  ',
            '97-112) ',
            '113-128)',
        ]

    # Subroutine in psas 3 for AGC4 to set in print the definition of a symbol or the upper limit of an
    # item in the availability display. Supply an integer in eqivlent or ones if there is no definition.
    # Sets up the definition using bank notation, or sets up four blots if no definition.
    def m_edit_def(self, eqivlent, col_start=0):
        if eqivlent == ONES:
            # Print blots and exit.
            self._line.text = self._line.text[:col_start+8] + '       ■■■■     ' + self._line.text[col_start+24:]
            return

        # Branch if location is not in a bank.
        if eqivlent > 0o5777:
            # Set bank number in print.
            bank_no = eqivlent >> 10
            self._line.text = self._line.text[:col_start+12] + ('%02o,' % bank_no) + self._line.text[col_start+15:]

            # Put subaddress in the range 6000-7777.
            eqivlent &= ~0o76000
            eqivlent |= 0o6000            

        # Set subaddress in print and exit.
        self._line.text = self._line.text[:col_start+15] + ('%04o' % eqivlent) + self._line.text[col_start+19:]

    # Subroutine in pass 3 for AGC4 to set in print the upper address limit, paragraph limit, stick number
    # and sense wire numbers for the paragraph summary.
    def m_print_pn(self, par_num, eqivlent):
        self._line.text = self._line.text[:24] + ('PARAGRAPH # %03o         ' % par_num) + self._line.text[48:]

        stick_no = (par_num >> 2) & 0xF
        if stick_no == 0:
            type_str = ''
            # Branch if paragraphs 001-003.
            if par_num == 0:
                type_str += 'SPECIAL AND CENTRAL REGISTERS & '
            type_str += 'ERASABLE MEMORY'

            self._line.text = self._line.text[:48] + type_str + self._line.text[48+len(type_str):]
            return self.m_edit_def(eqivlent)

        stick_no -= 1

        module, stick = self._stick_nos[stick_no]
        self._line.text = self._line.text[:48] + ('  MODULE %s    ' % module) + self._line.text[64:]
        self._line.text = self._line.text[:64] + ('STICK # %s     ' % stick) + self._line.text[80:]

        # Set up sense line set number.
        wire_no = (par_num >> 4) & 0o4
        wire_no |= (par_num & 3)

        self._line.text = self._line.text[:80] + \
                          ('SENSE LINE SET %u (WIRES %s' % (wire_no, self._wire_nos[wire_no])) + \
                          self._line.text[112:]

        return self.m_edit_def(eqivlent)

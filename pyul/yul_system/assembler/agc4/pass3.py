from yul_system.assembler.pass3 import Pass3
from yul_system.types import ONES

class Agc4Pass3(Pass3):
    def __init__(self, mon, yul, old_line, m_typ_tab, wd_recs):
        super().__init__(mon, yul, old_line, m_typ_tab, wd_recs)

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

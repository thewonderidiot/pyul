from yul_system.assembler.pass3 import Pass3
from yul_system.types import ONES, BAD_WORD, CONFLICT, SwitchBit

class Agc4Pass3(Pass3):
    def __init__(self, mon, yul, old_line, m_typ_tab, wd_recs):
        super().__init__(mon, yul, old_line, m_typ_tab, wd_recs)

        self._pret_flag = 0o1000000000
        self._cons_flag = 0o2000000000
        self._misc_flag = 0o3000000000
        self._flag_mask = 0o7000000000

        self._octal_ctr = -1
        self._n_oct_errs = 0
        self._checksum = 0

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

    def m_edit_wd(self, word):
        self._octal_ctr += 1
        image = ' '*14

        # Branch if not "BAD WORD" or "CONFLICT":
        if word in (BAD_WORD, CONFLICT):
            # Mark as such, go to set flag and exit.
            image = '%14s' % ('BAD WORD' if word == BAD_WORD else 'CONFLICT')
            return (image, 0o4000000000)

        flag = word & self._flag_mask
        avail = False
        if flag == self._pret_flag:
            image = image[:4] + 'I:' + image[6:]
        elif flag == self._cons_flag:
            image = image[:4] + 'C:' + image[6:]
        elif flag == self._misc_flag:
            # Branch if not referring to fixed memory.
            dest = (word >> 1) & 0o7777
            if dest >= 0o2000:
                if dest >= 0o6000:
                    bank_no = (word >> 31) & 0o77
                    dest = (bank_no << 10) + (dest & 0o1777)
                avail = self.avail_q(dest)

            if not avail:
                # Remove flag if refers to used fixed.
                word &= ~self._flag_mask
            else:
                image = image[:2] + '■REF' + image[6:]
                self._n_oct_errs += 1
                # Print remainder of octal storage map.
                self._yul.switch &= ~SwitchBit.SUPPRESS_OCTAL

        image = image[:7] + '%05o %o' % ((word >> 1) & 0o77777, word & 1)

        return image, word

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

    # Subroutine in pass 3 for AGC4 to print two explanatory lines at the head of each page of
    # an octal paragraph listing.
    def m_explain(self, par_num):
        self._page_hed2.text = ('OCTAL LISTING OF PARAGRAPH # %03o, WITH P' + \
                                'ARITY BIT IN BINARY AT THE RIGHT OF EACH' + \
                                ' WORD; "@" DENOTES UNUSED FIXED MEMORY. ') % par_num

        self._line.spacing = 2
        self._line.text = 'ALL VALID WORDS ARE BASIC INSTRUCTIONS E' + \
                          'XCEPT THOSE MARKED "I" (INTERPRETIVE OPE' + \
                          'RATOR WORDS) OR "C" (CONSTANTS).        '
        self.print_lin()

from yul_system.assembler.pass3 import Pass3
from yul_system.types import ONES, BAD_WORD, CONFLICT, Bit, SwitchBit

class Agc4Pass3(Pass3):
    def __init__(self, mon, yul, old_line, m_typ_tab, wd_recs):
        super().__init__(mon, yul, old_line, m_typ_tab, wd_recs)

        self._pret_flag = 0o1000000000
        self._cons_flag = 0o2000000000
        self._misc_flag = 0o3000000000
        self._flag_mask = 0o7000000000

        self._next_eqiv = 0
        self._l_tc_self = 0
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

    def m_edit_wd(self, word, address):
        image = ' '*14

        # Branch if not "BAD WORD" or "CONFLICT":
        if word in (BAD_WORD, CONFLICT):
            # Mark as such, go to set flag and exit.
            self._checksum = ONES
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
                self.p3_errors()

        image = image[:7] + '%05o %o' % ((word >> 1) & 0o77777, word & 1)

        # Branch if location is in fixed memory.
        if address < 0o2000:
            # Set flag and exit if used. Otherwise send all blanks and ditto.
            if word == 0:
                image = ' '*14
            self._checksum = ONES
            return image, word

        # For immediate missing-paragraph check.
        m_common = self._next_eqiv
        # Set criterion for missing-parag. check.
        self._next_eqiv = address + 1

        # Branch if not the beginning of a bank.
        if (address & 0o1777) == 0:
            self._checksum = 0
            return self.tc_self_q(word, address, image)

        # Branch if paragraph(s) missing.
        if address != m_common:
            # Response to discovery that one or more paragraphs are missing... effect on checksum processing.
            # Branch if new ph must be in new bank.
            if (m_common & 0o1777) != 0:
                m_common = (m_common & ~0o1777) | (address & 0o1777)
                # Branch if new paragraph is in new bank.
                if address == m_common:
                    # Branch if no summing to be done.
                    if self._checksum >= Bit.BIT1:
                        return self.no_suming(image, word, address)

            # Branch to apply prefix "NOSUM" to word.
            if word != 0:
                # Show no checksum in full bank, exit.
                image = ' NOSUM' + image[6:]
            else:
                # But for empty word write "NO CHECKSUM"
                image = '   NO CHECKSUM'
            self._checksum = ONES
            return image, word

        # Branch if no summing to be done.
        if self._checksum >= Bit.BIT1:
            return self.no_suming(image, word, address)

        # Branch if checksum must be planted now.
        if self._checksum >= Bit.BIT2:
            return self.plant_sum(image, word, address)

        # Branch if not end of bank.
        if (address & 0o1777) != 0o1777:
            return self.tc_self_q(word, address, image)

        # Branch to plant sum in lone hole at end.
        if word == 0:
            return self.plant_sum(image, word, address)

        # Show no checksum in full bank, exit.
        image = ' NOSUM' + image[6:]
        return image, word

    def no_suming(self, image, word, address):
        # Branch on used word when not summing.
        if word == 0:
            # Exit with AT for unused fixed.
            image = image[:6] + '   @    '
            return image, word

        # Exit if summing was given up.
        if self._checksum >= ONES:
            return image, word

        # Flag and exit if it's the extend const.
        if not (address == 0o5777 and word == 0o2000117776):
            # "■EOB" for used word after checksum.
            image = '  ■EOB' + image[6:]
            self.p3_errors()
            self._checksum = ONES

        return image, word

    def plant_sum(self, image, word, address):
        # Branch if used wd where cksm should go.
        if word != 0:
            return self.sum_error(image, word)

        # Form positive bank number. Checksum is such that total
        # sum is + or - bank no.
        bank_no = (address >> 10) & 0o37
        self._checksum &= ~Bit.BIT2

        # Branch if checksum is positive.
        if self._checksum > 0o37777:
            # Give bank number AGC sign of checksum.
            bank_no ^= 0xFFFF

        checksum = self._checksum - bank_no

        # Branch if alg. val. of cksm is plus.
        if checksum >= 0:
            checksum = abs(checksum) ^ 0o77777

        parity = 1
        for i in range(16):
            parity ^= ((checksum >> i) & 1)

        # Shift checksum and insert parity bit.
        word = checksum * 2 + parity
        # Print with prefix "CKSM".
        image = '  CKSM %05o %o' % (checksum, parity)

        # Show that sum is done and exit.
        self._checksum = Bit.BIT1
        return image, word

    def p3_errors(self):
        self._n_oct_errs += 1
        # Print remainder of octal storage map.
        self._yul.switch &= ~SwitchBit.SUPPRESS_OCTAL

    # Procedure in edit wd to watch for two TC selfs in succession, to make the checksum follow them.
    def tc_self_q(self, word, address, image):
        m_common = (word >> 1) & 0o77777
        # Branch if location is in a bank.
        if address < 0o6000:
            tc_self = address
        else:
            tc_self = 0o6000 | (address & 0o1777)

        # Branch if not an instruction.
        if m_common == tc_self and image[:6].isspace():
            # Branch if this is 2nd TC self in a row.
            if address != self._l_tc_self:
                self._l_tc_self = self._next_eqiv
                return self.add_2_sum(image, word)

            # Branch if TC selfs not at end of paragr.
            if (address & 0o377) != 0o377:
                return self.add_2_sum(image, word, request=True)

            # Look in substrab for next paragraph.
            par_id = (address + 1) // 256
            # Branch if next paragraph exists.
            if par_id in self._paragraphs:
                return self.add_2_sum(image, word, request=True)

            return self.sum_error(image, word)

        if word != 0:
            return self.add_2_sum(image, word)

        # '   NO CHECKSUM' for unused word that prevents formation of a checksum.
        image = '   NO CHECKSUM'
        self._checksum = ONES

        return image, word

    def sum_error(self, image, word):
        # "■SUM" for fouled-up checksum request.
        image = '  ■SUM' + image[6:]
        self.p3_errors()

        # Prepare post-checksum tests, exit.
        self._checksum = Bit.BIT1
        return image, word

    def add_2_sum(self, image, word, request=False):
        if request:
            # Request checksum in next word.
            self._checksum |= Bit.BIT2

        # Put word into sign-duplicated form.
        m_common = (word & 0o100000) | ((word >> 1) & 0o77777)
        self._checksum += m_common

        # Test for end-around carry and overflow.
        bits = (self._checksum >> 14) & 0o7

        if   bits == 0b000: # No EAC, +, no ovflo.
            pass
        elif bits == 0b001: # No EAC, +,    ovflo.
            self._checksum -= 0o37777
        elif bits == 0b010: # Impossible.
            pass
        elif bits == 0b011: # No EAC, -, no ovflo.
            pass
        elif bits == 0b100: #    EAC, +, no ovflo.
            self._checksum -= 0xFFFF
        elif bits == 0b101: # Impossible.
            pass
        elif bits == 0b110: #    EAC, -,    ovflo.
            self._checksum += 0o37777
            self._checksum -= 0xFFFF
        elif bits == 0b111: #    EAC, -, no ovflo.
            self._checksum -= 0xFFFF

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

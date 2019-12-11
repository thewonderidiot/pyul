from yul_system.types import Bit, SwitchBit, Line

class Pass3:
    def __init__(self, mon, yul, old_line):
        self._mon = mon
        self._yul = yul

        self._line = Line()
        self._old_line = old_line
        self._lin_count = 0

        self._page_hed2 = Line('SYMBOL TABLE LISTING, INCLUDING PAGE NUM' +
                               'BER OF DEFINITION, AND NUMBER OF REFEREN' +
                               'CES WITH FIRST AND LAST PAGE NUMBERS    ', spacing=2)

        self._last_line = 'THE ASSEMBLY WAS NAWSTY MANUFACTURABLE BINARY RECORDS STORED ON YULPROGS'
        self._rej_rev = '  PRECEDING REVISION REMAINS ON '
        self._rej_vers = 'THE NEW VERSION IS NOT FILED ON '
        self._subl_head = 'SUBROUTINE  REV#  CALLED  BEGINS'
        self._sub_lastl = '              THIS SUBROUTINE IS MAINTAINED IN SYMBOLIC FORM ON '
        self._joyful = ['   GOOD ', '   FAIR ', '    BAD ', '  LOUSY ', ' ROTTEN ', 'BILIOUS ']
        self._alt_words = [' SUPERB ', '  SO-SO ', ' DISMAL ', '  AWFUL ', '   VILE ', ' PUTRID ']

    def p3_masker(self):
        if self._yul.sym_thr.count() > 0:
            return self.read_syms()
        else:
            # Announce lack of symbols.
            self._line.text = 'THERE ARE NO SYMBOLS IN THIS ASSEMBLY.' + self._line.text[38:]
            self.print_lin()

    # Routine to pick symbols out of the symbol table in alphabetical order.
    def read_syms(self):
        pass

    # Subroutine in pass 3 to print a line with pagination control.
    # Strictly speaking, this subroutine prints the last line delivered to it.
    def print_lin(self):
        # New line ages suddenly.
        old_line = self._old_line
        self._old_line = self._line

        # Branch if last line is skip.
        prin_skip = False
        if old_line.spacing & Bit.BIT1:
            prin_skip = True
        else:

            # Add to line count from last line.
            self._lin_count += old_line.spacing
            if self._lin_count > self._yul.n_lines:
                # Skip after last line at end of page.
                old_line.spacing = Bit.BIT1
                prin_skip = True

        if prin_skip:
            if self._yul.n_copies != 0:
                self.copy_prt5()

            self._mon.phi_print(old_line.text, spacing=old_line.spacing)

            self._yul.page_no += 1
            # Put page number alpha in page head.
            self._yul.page_head = self._yul.page_head[:116] + ('%4d' % self._yul.page_no)

            if self._yul.n_copies != 0:
                self.copy_prt5()

            self._mon.phi_print(self._yul.page_head, spacing=3)

            # Print subheading.
            if self._yul.n_copies != 0:
                self.copy_prt5()

            self._mon.phi_print(self._page_hed2.text, spacing=self._page_hed2.spacing)

        else:
            if self._yul.n_copies != 0:
                self.copy_prt5()

            self._mon.phi_print(old_line.text, spacing=old_line.spacing)

        # Old line discovers fountain of youth. And is moreover made clean again.
        self._line = Line()

    def copy_prt5(self):
        # FIXME: implement
        pass

    def inish_p3(self):
        # Put correct name of tape into last line.
        self._good_bad = self._last_line[:64] + self._yul.tape

        # Type "END YUL PASS 2"
        self._mon.mon_typer('END YUL PASS 2')

        # Clear subroutine name slot in page head.
        # FIXME: Only do if not reject or obsolete.
        self._yul.page_head = self._yul.page_head[:102] + '         ' + self._yul.page_head[111:]

        self._yul.sym_place = 3 * (self._yul.sym_thr.count() + 1) # FIXME: Add in SUBROS and COUNTS

        # Change rejection line in version assy.
        if self._yul.switch & SwitchBit.VERSION:
            self._rej_rev = self._rej_vers

        # Test whether recording binary records.
        if not self._yul.switch & SwitchBit.REPRINT:
            # Cause obsoleting of old revs of this pr.
            self._last_prog = self._yul.prog_name

        # Branch if doing program assembly.
        if self._yul.switch & SwitchBit.SUBROUTINE:
            # Fix subroutine list page subhead.
            self._subl_head = self._subl_head[:16] + ' '*8 + self._subl_head[24:]

            # Fix final assembly printout.
            self._last_line = self._sub_lastl + self._last_line[64:]
        else:
            # Generate a random bit in bit 47.
            page_ones = self._yul.page_no % 10
            page_ones ^= self._yul.sym_place

            if (page_ones & Bit.BIT47) == 0:
                self._joyful = self._alt_words

        # FIXME: Create BYPT, etc.

        return self.p3_masker()

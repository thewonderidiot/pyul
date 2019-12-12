from yul_system.types import ALPHABET, Bit, SwitchBit, Line

ONE_THIRD = 0o253
FULL_PAGE = 0o53576

class SymbolHealth:
    def __init__(self, flag, no_valid_loc, count=0):
        self.flag = flag
        self.no_valid_loc = no_valid_loc
        self.count = count

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
        self._sy_col_hdg = '  SYMBOL H   DEFINITION   REFERENCES F  '
        self._sub_lastl = '              THIS SUBROUTINE IS MAINTAINED IN SYMBOLIC FORM ON '
        self._joyful = ['   GOOD ', '   FAIR ', '    BAD ', '  LOUSY ', ' ROTTEN ', 'BILIOUS ']
        self._alt_words = [' SUPERB ', '  SO-SO ', ' DISMAL ', '  AWFUL ', '   VILE ', ' PUTRID ']

        self._sym_liner = ONE_THIRD * 2

        self._owed_sym = None
        self._sym_letter = 'x'

        self._symh_vect = [
            SymbolHealth('U ', True),
            SymbolHealth('N ', True),
            SymbolHealth('NM', True),
            SymbolHealth('= ', False),
            SymbolHealth('=M', False),
            SymbolHealth('E ', True),
            SymbolHealth('J ', True),
            SymbolHealth('  ', False),
            SymbolHealth('M ', False),
            SymbolHealth('O ', True),
            SymbolHealth('T ', False),
            SymbolHealth('C ', False),
            SymbolHealth('OM', True),
            SymbolHealth('TM', False),
            SymbolHealth('CM', False),
            SymbolHealth('MM', True),
            SymbolHealth('X ', True),
        ]

    def p3_masker(self):
        if self._yul.sym_thr.count() > 0:
            return self.read_syms(self.print_sym, self.end_pr_sym)
        else:
            # Announce lack of symbols.
            self._line.text = 'THERE ARE NO SYMBOLS IN THIS ASSEMBLY.' + self._line.text[38:]
            self.print_lin()

    # Routine to pick symbols out of the symbol table in alphabetical order.
    def read_syms(self, found_sym, all_done):
        sym_names = self._yul.sym_thr.names()
        sym_names = sorted(sym_names, key=lambda sym: [ALPHABET.index(c) for c in sym])
        for name in sym_names:
            for sym in self._yul.sym_thr.all(name):
                found_sym(sym)

        all_done()

    def print_sym(self, sym):
        # Branch if symbol table is suppressed.
        if self._yul.switch & SwitchBit.SUPPRESS_SYMBOL:
            if sym.health == 6:
                # Count good symbols during suppression.
                self._symh_vect[7].count += 1
                return
            elif sym.health == 3:
                # Count good symbols during suppression.
                self._symh_vect[3].count += 1
                return
            # If not = either, print it anyway.

        # Branch if a page is under construction.
        if 0o700 <= self._sym_liner:
            if sym.name[0] != self._sym_letter:
                # Owe symbol while printing a divider.
                self._owed_sym = sym
                sym = None
        else:
            # Start new page by copying received sym.
            self._sym_letter = sym.name[0]

            # Point ot begining of page constr. area.
            self._l_bank_5 = []

        return self.pl_thread(sym)

    def pl_thread(self, sym):
        # Plant pointer to symbol table entry.
        self._l_bank_5.append(sym)

        # Count up thirds of lines.
        self._sym_liner += ONE_THIRD
        # Branch if constructed page is not full.
        if self._sym_liner <= FULL_PAGE:
            return self.owe_sym_q()

        return self.sym_page()

    def owe_sym_q(self):
        # Br. if a symbol is owed (new 1st ltr).
        if self._owed_sym is None:
            # Restore address, fetch another symbol.
            return

        # Set it up for first-letter comparison.
        self._sym_letter = self._owed_sym.name[0]
        owed_sym = self._owed_sym
        
        # Clear flag, go to process owed symbol.
        self._owed_sym = None
        return self.pl_thread(owed_sym)

    def sym_page(self):
        # Form number of lines of symbol info.
        sym_lines = (self._sym_liner >> 9) & 0o77
        # Form key to no. of symbols in last line.
        sym_liner = (self._sym_liner >> 7) & 0o3

        # Column headings for left third.
        self._line.text = self._sy_col_hdg + self._line.text[40:]
        if sym_lines > 1 or sym_liner > 0:
            # Plant vertical divider and column headings for middle third.
            self._line.text = self._line.text[:39] + '■' + self._sy_col_hdg + self._line.text[80:]

        if sym_lines > 1 or sym_liner > 1:
            # Plant vertical divider and column headings for right third.
            self._line.text = self._line.text[:79] + '■' + self._sy_col_hdg

        self._line.spacing = 1
        self.print_lin()

        # Line with just dividers after col hdgs.
        self._line.text = self._line.text[:39] + '■' + self._line.text[40:79] + '■' + self._line.text[80:]
        self._line.spacing = 1
        self.print_lin()

        # Point to beginning of second column.
        col2 = sym_lines
        # Point to beginning of third column.
        col3 = col2 + sym_lines
        # Branch if last line has over one column.
        if sym_liner == 0:
            col3 -= 1

        # Initialize comparison regs to blanks.
        compares = ['', '', '']

        # FIXME: REMOVE
        self._sym_liner = ONE_THIRD*2

    def end_pr_sym(self):
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

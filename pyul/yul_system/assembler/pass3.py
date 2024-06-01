from math import ceil
from yul_system.types import ALPHABET, Bit, SwitchBit, Line, ONES, MemType, CONFLICT

ONE_THIRD = 0o253
FULL_PAGE = 0o53576
EARLY_FULL_PAGE = 0o62607

class SymbolHealth:
    def __init__(self, flag, no_valid_loc, description, count=0):
        self.flag = flag
        self.no_valid_loc = no_valid_loc
        self.description = description
        self.count = count

class Paragraph:
    def __init__(self, number):
        self.number = number
        self.words = [0]*256

    def __getitem__(self, i):
        return self.words[i]

    def __setitem__(self, i, v):
        self.words[i] = v

    def asdict(self):
        return {
            'PARAGRAPH': self.number,
            'WORDS': self.words,
        }

class Pass3:
    def __init__(self, mon, yul, old_line, m_typ_tab, wd_recs):
        self._mon = mon
        self._yul = yul

        self._line = Line()
        self._old_line = old_line
        self._old_line.spacing = Bit.BIT1
        self._lin_count = 0
        self._n_oct_errs = 0

        self._m_typ_tab = m_typ_tab
        self._wd_recs = wd_recs

        self._paragraphs = {}

        if self._mon.year <= 1965:
            self._last_line = 'THE ASSEMBLY WAS NAWSTY  BINARY RECORDS FROM IT WERE WRITTEN ON %-8s' % self._yul.tape
            self._good = ' GOOD.  '
            self._fair = ' FAIR.  '
            self._bad = ' BAD. NO'
            self._page_hed2 = Line(' SYMBOL    DEFINITION   HEALTH OF DEFINI' +
                                'TION                                    ' +
                                '                   PAGE                 ', spacing=2)
        else:
            self._last_line = 'THE ASSEMBLY WAS NAWSTY MANUFACTURABLE BINARY RECORDS STORED ON %-8s' % self._yul.tape
            self._good = ' GOOD:  '
            self._fair = ' FAIR:  '
            self._bad = ' BAD: UN'
            self._page_hed2 = Line('SYMBOL TABLE LISTING, INCLUDING PAGE NUM' +
                                'BER OF DEFINITION, AND NUMBER OF REFEREN' +
                                'CES WITH FIRST AND LAST PAGE NUMBERS    ', spacing=2)

        self._last_line = '%-120s' % self._last_line

        self._rej_rev = '  PRECEDING REVISION REMAINS ON '
        self._rej_vers = 'THE NEW VERSION IS NOT FILED ON '
        self._subl_head = 'SUBROUTINE  REV#  CALLED  BEGINS'
        self._sy_col_hdg = '  SYMBOL H   DEFINITION   REFERENCES F  '
        self._sub_lastl = '              THIS SUBROUTINE IS MAINTAINED IN SYMBOLIC FORM ON '
        self._joyful = ['   GOOD ', '   FAIR ', '    BAD ', '  LOUSY ', ' ROTTEN ', 'BILIOUS ']
        self._alt_words = [' SUPERB ', '  SO-SO ', ' DISMAL ', '  AWFUL ', '   VILE ', ' PUTRID ']
        self._usym_cuss = 'UNDEFINED:'

        self._m_type_cax = [
            'SPECIAL OR NONEXISTENT MEMORY',
            'RESERVED FIXED MEMORY',
            'AVAILABLE FIXED MEMORY',
            'RESERVED ERASABLE MEMORY',
            'AVAILABLE ERASABLE MEMORY'
        ]

        self._sym_liner = ONE_THIRD * 2

        self._owed_sym = None
        self._sym_letter = 'x'

        self._eecr_list = []

        self._symh_vect = [
            SymbolHealth('U ■', True,  'UNDEFINED'),
            SymbolHealth('N ■', True,  'NEARLY DEFINED BY EQUALS'),
            SymbolHealth('NM■', True,  'MULTIPLY DEFINED INCLUDING NEARLY BY EQUALS'),
            SymbolHealth('= ■', False, 'DEFINED BY EQUALS'),
            SymbolHealth('=M■', False, 'MULTIPLY DEFINED INCLUDING BY EQUALS'),
            SymbolHealth('E ■', True,  'LEFTOVER WHICH FAILED TO FIT IN ERASABLE MEMORY'),
            SymbolHealth('J ■', True,  'LEFTOVER WHICH FAILED TO FIT IN FIXED MEMORY'),
            SymbolHealth('  ■', False, 'NORMALLY DEFINED'),
            SymbolHealth('M ■', False, 'GIVEN MULTIPLE DEFINITIONS'),
            SymbolHealth('O ■', True,  'OVERSIZE- OR ILL-DEFINED'),
            SymbolHealth('T ■', False, 'ASSOCIATED WITH WRONG MEMORY TYPE'),
            SymbolHealth('C ■', False, 'ASSOCIATED WITH CONFLICT IN FIXED OR ERASABLE MEMORY'),
            SymbolHealth('OM■', True,  'MULTIPLY DEFINED; OVERSIZE- OR ILL-DEFINED'),
            SymbolHealth('TM■', False, 'MULTIPLY DEFINED; ASSOCIATED WITH WRONG MEMORY TYPE'),
            SymbolHealth('CM■', False, 'MUTLIPLY DEIFNED; ASSOCIATED WITH CONFLICT IN FIXED OR ERASABLE MEMORY'),
            SymbolHealth('MM■', True,  'MULTIPLE ERRORS'),
            SymbolHealth('X ■', True,  'IN MISCELLANEOUS TROUBLE'),
            SymbolHealth('■■■', True,  'FAILED TO FIT IN SYMBOL TABLE'),
            SymbolHealth('=? ', False, 'DEFINED BY EQUALS BUT NEVER REFERRED TO'),
        ]

    def p3_masker(self):
        if self._yul.sym_thr.count() > 0:
            self.read_syms(self.print_sym, self.end_pr_sym)
        else:
            # Announce lack of symbols.
            self._line[0] = 'THERE ARE NO SYMBOLS IN THIS ASSEMBLY.'
            self.print_lin()

        self.av_disply()
        self.ws3()
        self.prin_pars()
        self.print_oct()
        self.subr_list()
        self.close_yul()

    # Routine to pick symbols out of the symbol table in alphabetical order.
    def read_syms(self, found_sym, all_done):
        sym_names = self._yul.sym_thr.names()
        sym_names = ['%-8s' % name for name in sym_names]
        sym_names = sorted(sym_names, key=lambda sym: [ALPHABET.index(c) for c in sym])
        for name in sym_names:
            for sym in self._yul.sym_thr.all(name.strip()):
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

        if self._mon.year <= 1965:
            return self.early_print_sym(sym)

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
        if self._mon.year <= 1965:
            return self.early_sym_page()

        # Form number of lines of symbol info.
        sym_lines = (self._sym_liner >> 9) & 0o77
        # Form key to no. of symbols in last line.
        sym_liner = (self._sym_liner >> 7) & 0o3

        # Column headings for left third.
        self._line[0] = self._sy_col_hdg
        if sym_lines > 1 or sym_liner > 0:
            # Plant vertical divider and column headings for middle third.
            self._line[39] = '■' + self._sy_col_hdg

        if sym_lines > 1 or sym_liner > 1:
            # Plant vertical divider and column headings for right third.
            self._line[79] = '■' + self._sy_col_hdg

        self._line.spacing = 1
        self.print_lin()

        # Line with just dividers after col hdgs.
        self._line[39] = '■' + self._line[40:79] + '■'
        self._line.spacing = 1
        self.print_lin()

        # Point to beginning of second and third columns.
        col_starts = [0, sym_lines, 2*sym_lines]
        # Branch if last line has over one column.
        if sym_liner == 0:
            col_starts[2] -= 1

        # Initialize comparison regs to blanks.
        compares = ['', '', '']

        for line in range(0, sym_lines):
            # Each third of a line ocntains all the information about one symbol.
            max_col = 3 if line < (sym_lines - 1) else min(sym_liner + 1, 3)
            for col in range(max_col):
                # Point to a symbol in the table
                sym_idx = col_starts[col] + line
                sym = self._l_bank_5[sym_idx]
                cc = col*40
                nc = (col+1)*40

                # Branch if symbol, not horizontal divider.
                if sym is None:
                    # Place horizontal divider of blots.
                    self._line[cc] = ('■'*36 + '   ' + '■')
                else:
                    # Branch if any of healths 0-4.
                    health = sym.health
                    if (sym.health >= 6) or ((sym.health == 5) and True): # FIXME: check for failed leftover erase
                        # Increment healths 5.5 (failed j-card) up.
                        health += 1

                    # Increment count of syms in this state.
                    self._symh_vect[health].count += 1

                    # Plant health flag and vertical divider.
                    self._line[cc+37] = self._symh_vect[health].flag

                    # Branch if symbol has a valid definition.
                    if self._symh_vect[health].no_valid_loc:
                        # Otherwise put it in typing list.
                        self.usy_place(sym)
                        eqivlent = ONES
                    else:
                        eqivlent = sym.value

                    # Set definition or blots in print.
                    self.m_edit_def(eqivlent, col_start=cc)

                    # Branch if different from last symbol in this column; otherwise print a ditto.
                    if sym.name == compares[col]:
                        self._line[cc] = '     "  '
                    else:
                        # Plant new symbol for next comparison.
                        compares[col] = sym.name

                        # Set headed symbol in print.
                        self._line[cc+2] = '%-8s' % sym.name

                    # Branch unless symbol was simply undef.
                    if sym.health < 3:
                        # Show that there's no page of definition.
                        self._line[cc+21] = ' - '
                    else:
                        # Convert page of def to zero-supp alpha.
                        self._line[cc+21] = '%3d' % sym.def_page

                    # Branch if symbol was referred to.
                    refs = len(sym.ref_pages)
                    if refs == 0:
                        # Show lack of references.
                        self._line[cc+24] = '  -   -   - '
                    else:
                        # Convert number of references to z/s alf.
                        refs_alf = '%3d' % refs

                        # Branch if 999 refs or fewer.
                        if refs > 999:
                            refs_alf = '>1K'

                        self._line[cc+25] = refs_alf

                        # Convert page of first ref to z/s alpha.
                        self._line[cc+28] = '%4d' % sym.ref_pages[0]

                        # When both page numbers are the same, print only the first one.
                        if sym.ref_pages[0] != sym.ref_pages[-1]:
                            # Convert page of last ref to z/s alpha.
                            self._line[cc+32] = '%4d' % sym.ref_pages[-1]

                    # Branch if any definition exists.
                    if eqivlent != ONES:
                        self.eecr_test(sym)

            # Remove vertical divider from last col.
            self._line[max_col*40-1] = ' '

            self._line.spacing = 1
            self.print_lin()

        self._old_line.spacing = 2
        self._line[0] = 'KEY: SYMBOLS DEFINED BY EQUALS ARE FLAGG' + \
                        'ED =.  OTHERS ARE NORMALLY DEFINED EXCEP' + \
                        'T THOSE FLAGGED:                        '
        self._line.spacing = 2
        self.print_lin()

        # Print key to health flags at end page.
        self._line[0] = 'U UNDEFINED             E FAILED LEFTOVE' + \
                        'R ERASE   M MULTIPLY DEFINED           T' + \
                        ' WRONG MEMORY TYPE    MM MULTIPLE ERRORS'
        self._line.spacing = 1
        self.print_lin()

        self._line[0] = 'N NEARLY DEFINED BY =   J FAILED LEFTOVE' + \
                        'R WORD    D OVERSIZE- OR ILL-DEFINED   C' + \
                        ' CONFLICT IN MEMORY   K  MISC. TROUBLE  '
        self._line.spacing = Bit.BIT1
        self.print_lin()

        # Show that no page is under construction.
        self._sym_liner = ONE_THIRD*2

    def early_sym_page(self):
        self._line.spacing = Bit.BIT1

        self.print_lin()
        self._sym_liner = ONE_THIRD * 2

    def early_print_sym(self, sym):
        # Branch if any of healths 0-4.
        health = sym.health
        if (sym.health >= 6) or ((sym.health == 5) and True): # FIXME: check for failed leftover erase
            # Increment healths 5.5 (failed j-card) up.
            health += 1
        if (sym.health == 3) and (len(sym.ref_pages) == 0):
            health = 18

        # Increment count of syms in this state.
        self._symh_vect[health].count += 1

        self._line[0] = sym.name

        # Branch if symbol has a valid definition.
        if self._symh_vect[health].no_valid_loc:
            # Otherwise put it in typing list.
            self.usy_place(sym)
            eqivlent = ONES
        else:
            eqivlent = sym.value

        # Set definition or blots in print.
        self.m_edit_def(eqivlent)

        self._line[24] = self._symh_vect[health].description
        self._line[99] = '%4u' % sym.def_page

        if self._old_line.spacing != Bit.BIT1:
            if self._old_line[0] != self._line[0]:
                self._old_line.spacing = 3
                self._sym_liner += ONE_THIRD * 6
            elif (ALPHABET.index(self._old_line[1]) // 16) != (ALPHABET.index(self._line[1]) // 16):
                self._old_line.spacing = 2
                self._sym_liner += ONE_THIRD * 3

        if self._sym_liner >= EARLY_FULL_PAGE:
            self._old_line.spacing = Bit.BIT1
            self._sym_liner = ONE_THIRD * 2

        self._sym_liner += ONE_THIRD * 3
        self.print_lin()

    def end_pr_sym(self):
        # Branch if sym tab listing filled last p.
        if self._sym_liner > 0o700:
            # Print last page of symbol table listing.
            self.sym_page()

        # Page heading for symbol table summary.
        self._page_hed2[0] = '%-120s' % 'SUMMARY OF SYMBOL TABLE LISTING'

        # Clean out print line in case of suppress.
        self._line.clear()

        # Symbol table overflow into health vectr.
        self._symh_vect[17].count = self._yul.sym_thr.sym_tab_xs

        # Branch if there are symbols to cuss.
        if len(self._usym_cuss) > 12:
            self._mon.mon_typer(self._usym_cuss)

        n_symbols = 0
        symh_vect = self._symh_vect[-1:] + self._symh_vect[:-1]
        for health in symh_vect:
            n_symbols += health.count
            if health.count > 0:
                # Convert count for this state to z/s alf.
                self._line.spacing = 2
                self._line[10] = ('%4d  ' % health.count)  + health.description
                self.print_lin()

        # Place a line between addends and total.
        self._line.spacing = 2
        self._line[10] = '----'
        self._old_line.spacing = 1
        self.print_lin()

        # Print grand total to finish summary.
        self._line[0] = ' TOTAL:   %4d' %  n_symbols
        self._line.spacing = 7
        self.print_lin()

        if self._mon.year > 1967:
            # Upspace 7 and print character set.
            self._line.spacing = Bit.BIT1
            self._line[0] = 'H-1800 CHARACTER SEQUENCE (360 LACKS ■≠½' + \
                            '␍⌑¢);  0123456789\'=: >&   +ABCDEFGHI:.)%' + \
                            '■?   -JKLMNOPQR#$*"≠½   </STUVWXYZ@,(␍⌑¢'
            self.print_lin()

        return self.eecr_tabl()

    def usy_place(self, sym):
        if len(self._usym_cuss) < 50:
            self._usym_cuss += '  %-8s  ' % sym.name
        elif len(self._usym_cuss) < 64:
            self._usym_cuss += '& MORE'

    def eecr_test(self, sym):
        # Branch when memory type is known.
        midx = 0
        while sym.value > self._m_typ_tab[midx][1]:
            midx += 1
        mem_type = self._m_typ_tab[midx][0]

        if mem_type != MemType.ERASABLE:
            # Exit if definition was not by equals.
            if sym.health >= 6:
                return
        lo = 0
        hi = len(self._eecr_list)
        idx = 0

        while lo < hi:
            idx = (lo + hi) // 2
            if sym.value >= self._eecr_list[idx].value:
                lo = idx + 1
            else:
                hi = idx

        self._eecr_list.insert(lo, sym)

    def eecr_tabl(self):
        if self._mon.year < 1967 or len(self._eecr_list) == 0:
            return self.wc_sumary()

        self._page_hed2[0] = 'ERASABLE & EQUIVALENCE CROSS-REFERENCE T' + \
                             'ABLE, SHOWING DEFINITION, PAGE OF DEFINI' + \
                             'TION, AND SYMBOL                        '

        eecr_page = 0
        for p in range(0, len(self._eecr_list), 200):
            eecrs = self._eecr_list[p:p+200]
            eecr_page = len(eecrs)
            # Number of eecrs in last line.
            excess = eecr_page % 5
            rows = eecr_page // 5

            for row in range(rows + (1 if excess > 0 else 0)):
                cols = excess if (row == rows) else 5
                sym_idx = row
                col_start = 0
                for col in range(cols):
                    sym = eecrs[sym_idx]

                    # Set definition of symbol in print.
                    self.m_edit_def(sym.value, col_start=col_start)

                    # Shift definition to left edge of column.
                    self._line[col_start] = self._line[col_start+11:col_start+19]

                    # Set page of definition in print.
                    self._line[col_start+9] = '%4d  ' % sym.def_page

                    # Set symbol in print.
                    self._line[col_start+15] = '%-8s' % sym.name

                    # Advance to head of next column.
                    sym_idx += rows
                    col_start += 24

                    # Branch if now on shorter columns.
                    if col < excess:
                        # Advance one more step on longer ones.
                        sym_idx += 1

                # Branch if now end of a 4-line group.
                if (row % 4) == 3:
                    self._line.spacing = 2
                else:
                    self._line.spacing = 1

                self.print_lin()

        return self.wc_sumary()

    def wc_sumary(self):
        # FIXME: Implement word count summary
        pass

    def av_disply(self):
        self._page_hed2[0] = '%-120s' % 'MEMORY TYPE & AVAILABILITY DISPLAY'

        # Initialize address to 0.
        address = 0

        # Two columns are built up in bank 5.
        self._l_bank_5 = []

        while address <= self._m_typ_tab[-1][1]:
            # Skip to H-O-F before each page
            self._old_line.spacing = Bit.BIT1

            # Branch when memory type found.
            midx = 0
            while address > self._m_typ_tab[midx][1]:
                midx += 1
            mem_type = self._m_typ_tab[midx][0]
            upper_lim = self._m_typ_tab[midx][1]
            end = address

            # Branch if not special or nonexistent.
            if mem_type == MemType.SPEC_NON:
                # Save address of description.
                desc = 0
                # Save end category = upper lim of entry.
                end = upper_lim

            else:
                avail = self.avail_q(address)
                if mem_type == MemType.FIXED:
                    if avail:
                        desc = 2
                    else:
                        desc = 1
                else:
                    if avail:
                        desc = 4
                    else:
                        desc = 3

                # Go to find end of reserved/available E or F.
                end += 1
                while end < upper_lim:
                    next_avail = self.avail_q(end)
                    if avail != next_avail:
                        end -= 1
                        break
                    end += 1

            self._l_bank_5.append((address, end, desc))
            address = end + 1
            # Branch if a pageful is ready.
            if (len(self._l_bank_5) >= 80) or (address > self._m_typ_tab[-1][1]):
                # Having stored up to 80 entries in condensed CAC-format, we now print them on one page in two columns.
                right_start = ceil(len(self._l_bank_5) / 2)
                for row in range(right_start):
                    cat_idx = row
                    cs = 0
                    for i in range(2):
                        start, end, desc_idx = self._l_bank_5[cat_idx]
                        # Store description of memory type.
                        desc = self._m_type_cax[desc_idx]
                        self._line[cs+24] = desc

                        # Print upper limit of category.
                        self.m_edit_def(end, col_start=cs)

                        # Stop there if length is 1.
                        if start != end:
                            self.m_edit_def(start, col_start=cs-12)

                            # Insert "TO" between low and high limits.
                            self._line[cs+9] = 'TO'

                        cat_idx += right_start
                        cs += 64
                        if cat_idx >= len(self._l_bank_5):
                            break

                    self._line.spacing = 2 if (row % 4 == 3) else 1
                    self.print_lin()

                self._l_bank_5 = []

    def avail_q(self, eqivlent):
        available = True

        avail_msk = 1 << (eqivlent & 0x1F)
        avail_idx = eqivlent >> 5

        if self._yul.av_table[avail_idx] & avail_msk:
            available = False

        return available

    def ws3(self):
        # FIXME: put symbol table into BYPT

        # Sort and merge word records
        self._wd_recs = sorted(self._wd_recs, key=lambda w: w.fwa)
        i = 0
        while i < (len(self._wd_recs) - 1):
            a = self._wd_recs[i]
            b = self._wd_recs[i+1]
            if (a.page == b.page) and (a.lwa == b.fwa - 1):
                a.words.extend(b.words)
                a.lwa = b.lwa
                self._wd_recs.pop(i+1)
            else:
                i += 1

        for page_group in range(0, len(self._wd_recs), 160):
            page_locs = self._wd_recs[page_group:page_group+160]
            n_locs = len(page_locs)

            # Form as much subhead as needed.
            self._page_hed2.clear()
            for i in range(min(4, n_locs)):
                self._page_hed2[i*32] = 'OCCUPIED LOCATIONS  PAGE'
            self._old_line.spacing = Bit.BIT1

            rows = n_locs // 4
            excess = n_locs % 4

            for row in range(rows + (1 if excess > 0 else 0)):
                cols = excess if (row == rows) else 4
                loc_idx = row
                for col in range(cols):
                    loc = page_locs[loc_idx]
                    # Set LWA in print.
                    self.m_edit_def(loc.lwa, col_start=col*32)

                    # Print LWA only if FWA = LWA.
                    if loc.fwa != loc.lwa:
                        self.m_edit_def(loc.fwa, col_start=col*32 - 12)
                        self._line[col*32+9] = 'TO'

                    # Set page number in print.
                    self._line[col*32+20] = '%4d' % loc.page

                    loc_idx += rows
                    if col < excess:
                        loc_idx += 1

                self._line.spacing = 2 if (row % 4 == 3) else 1
                self.print_lin()

        # Procedure to initialize each substrand, and sorting loop for each word record.
        for rec in self._wd_recs:
            par_id = rec.fwa // 256
            par_addr = rec.fwa % 256

            for word in rec.words:
                if par_id not in self._paragraphs:
                    self._paragraphs[par_id] = Paragraph(par_id)

                # Branch if no storage conflict.
                if self._paragraphs[par_id][par_addr] != 0:
                    # Conflict is enough for bad assembly.
                    self._yul.switch |= SwitchBit.BAD_ASSEMBLY
                    self._paragraphs[par_id][par_addr] = CONFLICT
                else:
                    self._paragraphs[par_id][par_addr] = word

                par_addr += 1
                if par_addr >= 256:
                    par_addr = 0
                    par_id += 1

    def prin_pars(self):
        # Skip to head of form after availability.
        self._old_line.spacing = Bit.BIT1

        # Page subhead for substrand summary.
        self._page_hed2[0] = 'PARAGRAPHS GENERATED FOR THIS ASSEMBLY; ' + \
                             'ADDRESS LIMITS AND THE MANUFACTURING LOC' + \
                             'ATION CODE ARE SHOWN FOR EACH.          '

        # In case of barren assembly (no words).
        if len(self._paragraphs) == 0:
            # Announce lack of words, go to finalize.
            self._line[0] = '%-120s' % 'NO WORDS WERE GENERATED FOR THIS ASSEMBLY.'
            self.print_lin()
            self._yul.switch |= SwitchBit.BAD_ASSEMBLY
            return

        last_ss_no = -1
        for i,p in self._paragraphs.items():
            self._line.spacing = 2
            # Branch if this ph not successor of last.
            if p.number == last_ss_no:
                # Branch if this ph begins 4-ph group.
                if (p.number & 3) != 0:
                    # Selectively close up ph summary format.
                    self._old_line.spacing = 1

            # Form 1st & last addresses of paragraph.
            address = p.number * 256
            eqivlent = address + 255

            # Print most paragraph information
            self.m_print_pn(p.number, eqivlent)

            # Call for lower limit print.
            self.m_edit_def(address, col_start=-12)

            # Insert "TO" between limit addresses.
            self._line[9] = 'TO'

            self.print_lin()

            last_ss_no = p.number + 1

        self.print_lin()

    def print_oct(self):
        # In case octal suppression is revoked.
        self._page_hed2[0] = '■■■■■■■■■■■ SUPPRESSION OF OCTAL STORAGE' + \
                             ' MAP REVOKED BECAUSE OF CUSSES (■XXX; EA' + \
                             'CH COUNTS AS A CUSSED LINE). ■■■■■■■■■■■'

        # Prepare for cusses in the octal stormap.
        n_oct_errs = 0

        for i,p in self._paragraphs.items():
            # Go to H-O-F for each par.
            self._old_line.spacing = Bit.BIT1

            # Skip if octal map is suppressed.
            if not self._yul.switch & SwitchBit.SUPPRESS_OCTAL:
                # Print page head and subhead for parags.
                self.m_explain(p.number)

            # From 1st address of paragraph.
            address = p.number * 256

            for l in range(32):
                # Set 1st address of line in print
                self.m_edit_def(address, col_start=-12)

                for w in range(8):
                    # Make up 14-charater print image of wd.
                    wno = l*8 + w
                    image, edited_word = self.m_edit_wd(p[wno], address + w)
                    p[wno] = edited_word

                    self._line[8+w*14] = image

                # Branch if not last of 4-line group.
                if (l % 4) == 3:
                    self._line.spacing = 2
                else:
                    self._line.spacing = 1

                # Skip to suppress octal storage map.
                if not self._yul.switch & SwitchBit.SUPPRESS_OCTAL:
                    # Print an address and eight words.
                    self.print_lin()

                address += 8

            # At end of each paragraph (formerly called a substrand), if any octal-map errors were found, print a
            # combination cuss-wham line giving the number(s) of the cuss(es) and the page of the preceding cussed line.

            if self._n_oct_errs > 0:
                # Serial no for first cuss of page.
                first_cuss = self._yul.n_err_lins + 1
                line_beg = 'E■■■■■■  # %d  ' % first_cuss

                # Line begins "E■■■■■■  # NN  "
                self._line[0] = line_beg

                # Fill it out as a wham line.
                self._line[16] = '■'*104

                # Branch if this is the first cuss page.
                if self._yul.err_pages[0] is not None:
                    # Set in print pointer to previous cuss.
                    self._line[80] = 'PRECEDING CUSSED LINE IS ON PAGE%4s ■■■' % self._yul.err_pages[1]
                else:
                    # Show that first cuss is on this page.
                    self._yul.err_pages[0] = self._yul.page_head[-4:]

                # Show that latest cuss is on this page.
                self._yul.err_pages[1] = self._yul.page_head[-4:]

                self._yul.n_err_lins += self._n_oct_errs

                # Cuss line is done if just one on page.
                if self._n_oct_errs > 1:
                    # Make it "E■■■■■■  # NN   THROUGH  # NN"
                    line_end = 'THROUGH  # %d' % self._yul.n_err_lins
                    self._line[16] = line_end

                # Skip if octal map is suppressed.
                if not self._yul.switch & SwitchBit.SUPPRESS_OCTAL:
                    self._line.spacing = 1
                    self.print_lin()

                # Reset count for next page.
                self._n_oct_errs = 0

    def subr_list(self):
        # Set up page subhead for subroutine list.
        self._page_hed2[0] = '%-120s' % self._subl_head

        # Initialize 4-lines-per-group counter.
        self._old_line.spacing = Bit.BIT1
        subro_no = 0

        # Clean line lest octl map was suppressed.
        self._line[0] = ' '*120

        # Begin by seeing if there are none.
        if len(self._yul.adhoc_subs) < 1:
            return

        for subro in self._yul.adhoc_subs:
            # Set subroutine name in print.
            self._line[0] = subro['NAME']
            # Set revision number in print.
            self._line[13] = '%3u' % subro['REVISION']

            # Branch if subro call was not confirmed.
            if subro['CALLED'] != 0:
                # Set in print page of confirming call.
                self._line[21] = '%3u' % subro['CALLED']

                # Branch if subroutine was not printed
                if subro['BEGINS'] != 0:
                    # Set in print page where subro begins.
                    self._line[29] = '%3u' % subro['BEGINS']

            self._line.spacing = 1
            if (subro_no & 3) == 3:
                # SP2 between groups of four lines
                self._line.spacing = 2

            subro_no += 1

            # Advance to next subroutine and print.
            self.print_lin()


    # Procedure for pass 3 to clean up the end of YULPROGS. If the assembly is a reprint or a rejected assy. or a
    # subroutine, YULPROGS has already been closed and rewound, and bit 11 set. Otherwise the existence of a bypt
    # record for the program is noted in the directory, unless the assembly is bad. The file tape is closed and rewound.
    def close_yul(self):
        # Branch if new BYPT records were written.
        # Branch if bad merge
        if (self._yul.switch & SwitchBit.REPRINT) and (self._yul.switch < SwitchBit.REPRINT_PASS1P5):
            self._line[0] = self._last_line
            self._line[0] = 'ALL INPUT CARDS WERE REJECTED.  '
            self._line[32] = self._rej_rev

            # Be most emphatic about rejection.
            self._mon.mon_typer('ALL INPUT CARDS REJECTED')
        else:
            # FIXME: Improve BYPT handling
            self._bypt['PARAGRAPHS'] = [{'PARAGRAPH': p.number, 'WORDS': p.words} for n,p in self._paragraphs.items()]

            # Let last line show filing on disc.
            if self._mon.disc:
                self._last_line = self._last_line[:54] + 'ON DISC &' + self._last_line[63:]
            
            # Degree of aspersion gives the bad news.
            ecch = False
            if self._yul.n_err_lins <= 2:
                horrid = self._joyful[2]
            elif self._yul.n_err_lins <= 9:
                horrid = self._joyful[3]
            elif self._yul.n_err_lins <= 99:
                horrid = self._joyful[4]
            elif self._yul.n_err_lins <= 999:
                horrid = self._joyful[5]
            else:
                ecch = True

            # Branch if subroutine, not program.
            self._line[0] = self._last_line

            if not self._yul.switch & SwitchBit.SUBROUTINE:
                # Admit to BYPT if good/fair prog assy.
                if self._yul.switch & SwitchBit.BAD_ASSEMBLY:
                    self._line[16] = self._bad
                    if ecch:
                        self._mon.mon_typer('YUCCCHHHH')
                    else:
                        self._mon.mon_typer(horrid + 'ASSEMBLY; FILED ON DISC')
                else:
                    self._bypt['MANUFACTURABLE'] = True
                    if self._yul.n_err_lins == 0:
                        self._line[16] = self._good
                        self._mon.mon_typer(self._joyful[0] + 'ASSEMBLY; FILED ON DISC')
                    else:
                        self._line[16] = self._fair
                        self._mon.mon_typer(self._joyful[1] + 'ASSEMBLY; FILED ON DISC')
            else:
                self._mon.mon_typer(' END OF ASSEMBLY; FILED ON DISC')

        # Branch if no errors in program.
        if self._yul.n_err_lins > 0:
            # Set error count in print.
            self._line[72] = ('%8d' % self._yul.n_err_lins) + \
                            ' LINES CUSSED BETWEEN PAGES' + \
                            self._yul.err_pages[0] + ' AND' +\
                            self._yul.err_pages[1] + '.'
            self._mon.mon_typer(self._line[72:])

        self._old_line.spacing = 4
        self._mon.mon_typer('', end='\n\n\n')

        # Don't let last line have a page to self.
        self._lin_count = 0

        # Print end of last ph or of subro list.
        self._line[72] = '.'
        self.print_lin()

        # Print last line of assembly output.
        self.print_lin()

        # Write BYPT to tape
        if not self._yul.switch & SwitchBit.REPRINT:
            self._yul.yulprogs.create_bypt(self._yul.comp_name, self._yul.prog_name, self._yul.revno, self._bypt)

        # FIXME: final closeout


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

            self._lin_count = 5

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

        self._bypt = {
            'MANUFACTURABLE': False,
            'PARAGRAPHS': [],
            'SYMBOLS': [],
        }

        self._yul.sym_thr.sort_multdefs()

        return self.p3_masker()

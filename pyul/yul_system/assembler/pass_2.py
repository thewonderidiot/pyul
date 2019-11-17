from yul_system.types import ALPHABET, ONES, Symbol, SwitchBit, HealthBit, FieldCodBit, Bit

class Cuss:
    def __init__(self, msg, poison=False):
        self.msg = msg
        self.poison = poison
        self.demand = False

class Line:
    def __init__(self, text=' '*120, spacing=0):
        self.spacing = spacing
        self.text = text

class Pass2:
    def __init__(self, mon, yul, adr_limit, m_typ_tab):
        self._mon = mon
        self._yul = yul
        self._adr_limit = adr_limit
        self._m_typ_tab = m_typ_tab
        self._def_xform = 0o31111615554
        self._marker = '*'
        self._lin_count = 0
        self._page_no = 0
        self._user_page = 0
        self._n_err_lins = 0
        self._min_adres = 0
        self._field_cod = [None, None]
        self._head = ' '
        self._line = Line()
        self._old_line = Line()
        self._user_log = Line(' '*81 + 'USER\'S OWN PAGE NO.' + 20*' ', spacing=2)
        self._card_typs = [
            (self.end_of,      2),
            (self.modify,      3),
            (self.end_error,   2),
            (self.card_no,     3),
            (self.accept,      2),
            (self.delete,      3),
            (self.remarks,     2),
            (self.disaster,    0),
            (self.no_loc_sym,  2),
            (self.memory,      3),
            (self.instruct,    2),
            (self.illegop,     2),
            (self.decimal,     0),
            (self.octal,       0),
            (self.equals,      3),
            (self.setloc,      3),
            (self.erase,       3),
            (self._2octal,     0),
            (self._2decimal,   0),
            (self.block,       3),
            (self.head_tail,   3),
            (self.too_late,    3),
            (self.subro,       3),
            (self.instruct_p1, 3),
            (self.even,        3),
            (self.count,       3),
            (self.segnum,      3),
        ]

    def pass_2(self):
        for popo in self._yul.popos:
            card_type = popo.health & HealthBit.CARD_TYPE_MASK

            # Branch if last card wasnt remarks
            if self._yul.switch & SwitchBit.LAST_REM:
                self.un_las_rem(popo, card_type)
            else:
                self.right_pq(popo, card_type)

    def un_las_rem(self, popo, card_type):
        self._yul.switch &= ~SwitchBit.LAST_REM
        # Branch if this card isnt right print.
        if card_type == HealthBit.CARD_TYPE_RIGHTP:
            # Branch if line unaffected by this rev.
            if popo.marked:
                self._old_line.text = self._old_line.text[:7] + self._marker + self._old_line.text[8:]
                self._marker = '*'

            self.send_sypt(popo.card)

            # Set right print remarks in print.
            self._old_line.text = self._old_line.text[:80] + popo.card[8:48]

            # Branch if no right print cardno error.
            if not popo.health & Bit.BIT7:
                return self.cusser()

            # Make up card number error note.
            self._line.text = self._line.text[:88] + self.cuss_list[0].msg
            if self.cuss_list[0].demand:
                return self.rem_cn_err(popo, card_type)

            # If 1st cuss of page, left end of blots.
            left_end = 2

            # Apply serial number to cuss.
            self.numb_cuss()
            return self.count_cus(left_end, 6)

        if self.cuss_list[0].demand:
            return self.rem_cn_err(popo, card_type)
        else:
            return self.right_pq(popo, card_type)

    def rem_cn_err(self, popo, card_type):
        # Cuss crd number error in remarks card.
        self.cuss_list[0].demand = 0
        left_end = self.prin_cuss(self.cuss_list[0])

        # Branch if this card is not right print.
        if card_type != HealthBit.CARD_TYPE_RIGHTP:
            self.count_cus(left_end, 10)
            return self.right_pq(popo, card_type)

        return self.count_cus(left_end, 6)

    # Procedure when last card was not left print remarks.
    def right_pq(self, popo, card_type):
        # Set up columns 1-7.
        self._line.text = popo.card[:7] + self._line.text[7:]

        # Branch if line affected by this revision
        if popo.marked:
            self._line.text = self._line.text[:7] + self._marker + self._line.text[8:]
            self._marker = '*'

        # Maybe cuss card number sequence error.
        if popo.health & Bit.BIT7:
            self.cuss_list[0].demand = True

        # Branch if card is not right print
        if card_type == HealthBit.CARD_TYPE_RIGHTP:
            # Print under 1st half of remarks field.
            self._line.text = self._line.text[:80] + popo.card[8:48]
            # Make right print a continuation card.
            self._line.text = 'C' + self._line.text[1:]
            self.no_loc_sym(popo)
            return

        vert_format = ord(popo.card[7]) & 0xF
        if vert_format == 8:
            # Maybe set up skip bit.
            self._line.spacing |= Bit.BIT1
        else:
            # Maybe set up space count.
            self._line.spacing |= vert_format

        # Set up columns 9-80.
        self._line.text = self._line.text[:48] + popo.card[8:]

        # Turn off leftover switch.
        self._yul.switch &= ~SwitchBit.LEFTOVER

        # Set up branches on card type.
        own_proc, ternary_key = self._card_typs[card_type // Bit.BIT6]

        # Use ternary key to check whether columns 1, 17, and 24 contain
        # queer information.
        if ternary_key == 3 or (ternary_key == 0 and popo.card[0] != 'J'):
            if popo.card[0] != ' ':
                self.cuss_list[60].demand = True
            if popo.card[16] != ' ':
                self.cuss_list[61].demand = True
            if popo.card[23] != ' ':
                self.cuss_list[62].demand = True

        own_proc(popo)

        return self.end_pass_2()

    def end_pass_2(self):
        pass

    def end_of(self, popo):
        pass

    def modify(self, popo):
        pass

    def end_error(self, popo):
        pass

    def card_no(self, popo):
        pass

    def accept(self, popo):
        pass

    def delete(self, popo):
        pass

    # Procedure in pass 2 for remarks cards. Postpones cussing to check for a right print card.
    def remarks(self, popo):
        # Move remark 5 words left. Fill out line with blanks.
        self._line.text = self._line.text[:8] + self._line.text[48:] + 40*' '
        # Signal that last was remarks, print.
        self._yul.switch |= SwitchBit.LAST_REM
        self.print_lin()
        self.send_sypt(popo)

    def disaster(self, popo):
        pass

    def no_loc_sym(self, popo, loc_symbol=None, print_line=True):
        if print_line:
            self.print_lin()
        return self.pag_loxim(popo, loc_symbol)

    def memory(self, popo):
        pass

    def instruct(self, popo):
        loc_symbol = self.instront(popo)
        self.m_proc_op(popo)
        self.proc_word(popo, loc_symbol)

    def illegop(self, popo):
        pass

    def decimal(self, popo):
        pass

    def octal(self, popo):
        pass

    # Subroutine in pass 2 to process the location field of an instruction or constant. Cusses about location
    # format and value, determines the value of a leftover location if required, and prints the location value
    # with end of block or bank notation if required.
    def instront(self, popo):
        # Branch if location is symbolic.
        if not popo.health & Bit.BIT8:
            # Maybe cuss rejection of leftover status.
            if popo.health & Bit.BIT13:
                self.cuss_list[3].demand = True
            # Maybe cuss "D" error, zero equaloc.
            if popo.health & Bit.BIT9:
                self.cuss_list[1].demand = True
            loc_symbol = None
        else:
            # Maybe cuss loc sym no fit in table.
            if popo.health & Bit.BIT15:
                self.cuss_list[14].demand = True

            # Analyze and pre-process location symbol.
            loc_symbol = self.loc_sym_1(popo)

        # Branch if loc symbol didn't fit in table.
        if loc_symbol is not None:
            # Maybe cuss wrongful predefinition.
            if popo.health & Bit.BIT13:
                self.cuss_list[51].demand = True
            # Put location symbol into cuss in case it was wrongfully predefined.
            self.sym_cuss(self.cuss_list[51], loc_symbol.name)

        # Maybe cuss oversize location value.
        if popo.health & Bit.BIT14:
            self.cuss_list[6].demand = True

        # Maybe cuss location memory type error.
        if popo.health & Bit.BIT15:
            self.cuss_list[5].demand = True

        # Maybe cuss conflict in location content.
        if popo.health & Bit.BIT16:
            self.cuss_list[4].demand = True

        no_loc_leftover = Bit.BIT8 | Bit.BIT12
        # Branch if there's no good location valu.
        if popo.health & Bit.BIT14:
            location = ONES
        # Branch if location not leftover or no location field symbol.
        elif (popo.health & no_loc_leftover) == no_loc_leftover:
            # Turn on leftover switch.
            self._yul.switch |= SwitchBit.LEFTOVER
            # Branch if the leftover was defined.
            if loc_symbol.defined:
                # Use value found by pass 1.5.
                popo.health |= loc_symbol.value & 0xFFFF
                self._location = popo.health & 0xFFFF
            else:
                self._location = ONES
        else:
            self._location = popo.health & 0xFFFF

        # Print location value and return.
        self.m_ploc_eb(self._location)

        return loc_symbol

    # Procedure in pass 2 for IS,=,EQUALS cards. Prints value, cusses for format, value, and both symbols.
    def equals(self, popo):
        # Maybe cuss  D  error.
        if popo.health & Bit.BIT9:
            self.cuss_list[1].demand = True

        # Maybe cuss unsymbolic loc field (that bit inverted in err/warn code).
        if not popo.health & Bit.BIT8:
            self.cuss_list[46].demand = True

        # Maybe cuss predefinition failure.
        if popo.health & Bit.BIT10:
            self.cuss_list[13].demand = True

        # Maybe cuss loc sym no fit in table.
        if popo.health & Bit.BIT15:
            self.cuss_list[14].demand = True

        # Maybe cuss meaningless address field.
        if popo.health & Bit.BIT13:
            self.cuss_list[8].demand = True

        # Maybe cuss address size error.
        if popo.health & Bit.BIT14:
            self.cuss_list[10].demand = True

        # Branch if location is symbolic.
        if self.cuss_list[46].demand:
            # Proclaim absence of location symbol.
            loc_symbol = None
        else:
            # Analyze and pre-process location symbol.
            loc_symbol = self.loc_sym_1(popo)

        # Branch if address symbol is in table.
        if popo.health & Bit.BIT16:
            adr_wd = self.adr_field(popo)
            # Form headed symbol.
            if len(adr_wd[0]) < 8:
                adr_wd[0] = ('%-7s%s' % (adr_wd[0], self._head)).strip()
            # Cuss fullness.
            self.sym_cuss(self.cuss_list[14], adr_wd[0])
            # Go to join end of setloc procedure.
            self.cuss_list[0].demand = True
            return self.form_locn(good_loc=False)

        # Recover address symbol information
        adr_symbol = self.fits_fitz(popo)
        # Branch if there is no address symbol.
        if adr_symbol is not None:
            # Call for address symbol cussing.
            self.symb_fits(adr_symbol)

        # Exit when no location symbol.
        if loc_symbol is None:
            return self.form_locn(good_loc=False)

        if loc_symbol.defined:
            self._location = loc_symbol.value
        else:
            self._location = ONES

        # Print location value.
        self.m_ploc_is(self._location)

        if loc_symbol.health >= 5:
            # Move location symbol for cussing by proc word, done for 5 through F.
            return self.health_cq(popo, loc_symbol)

        # Select local cussing procedure on 1 - 4.
        if loc_symbol.health == 1:
            self.cuss_list[28].demand = True
            self.sym_cuss(self.cuss_list[28], loc_symbol.name)
            return self.no_loc_sym(popo, loc_symbol)

        elif loc_symbol.health == 2:
            self.cuss_list[31].demand = True
            self.sym_cuss(self.cuss_list[31], loc_symbol.name)
            return self.no_loc_sym(popo, loc_symbol)

        elif loc_symbol.health == 3:
            self.print_lin()
            return self.pag_loxim(popo, loc_symbol, adr_symbol)

        else: #4
            self.cuss_list[32].demand = True
            self.sym_cuss(self.cuss_list[32], loc_symbol.name)
            return self.no_loc_sym(popo, loc_symbol)

    def pag_loxim(self, popo, loc_symbol=None, adr_symbol=None):
        page = self._page_no
        if self._yul.switch & SwitchBit.OWE_HEADS:
            # Compensates if page heads are owed.
            page += 1

        # Branch if no loc symbol in sym table.
        if loc_symbol is not None:
            # Record page on which symbol was defined.
            loc_symbol.def_page = page

        # Branch if no address symbol in sym tab.
        if adr_symbol is not None:
            adr_symbol.ref_pages.append(page)

            # Branch if this is not the first ref or doing a suppressed subroutine.
            if len(adr_symbol.ref_pages) > 1 and self._yul.switch & SwitchBit.PRINT:
                # Set in print page of last ref in alpha.
                self._old_line.text = (self._old_line.text[:16] + 'LAST' + ('%4d' % adr_symbol.ref_pages[-2]) +
                                    self._old_line.text[24:])

            ref_str = 'REF '
            if len(adr_symbol.ref_pages) > 999:
                # If over 999 references, set up "REF >1K".
                ref_str += '>1K '
            else:
                ref_str += '%3d ' % len(adr_symbol.ref_pages)

            # Set in print serial no. of ref in alpha.
            self._old_line.text = self._old_line.text[:8] + ref_str + self._old_line.text[16:]

        # Release card for tape and go to cuss.
        self.send_sypt(popo)
        return self.cusser()

    # Routine in pass 2 to finish processing a word (either an instruction or constant). Releases the line
    # for printing, transmits words to "SEND WORD" if the location is valid, sets up all cusses concerning the location
    # symbol if any, restores "NO LOC SYM" as a general end procedure, releases the card for transmission to tape as a
    # sypt or sylt record component, and proceeds to the universal cussing routine.
    def proc_word(self, popo, loc_symbol):
        # Release line for printing.
        self.print_lin()

        # Branch if there is no location symbol or loc sym not in symbol table.
        if not popo.health & Bit.BIT8 or loc_symbol is None:
            return self.no_loc_sym(popo, loc_symbol, print_line=False)

        return self.health_cq(popo, loc_symbol, print_line=False)

    def health_cq(self, popo, symbol, print_line=True):
        # Branch if symbol health is B or more.
        if symbol.health >= 0xB:
            # Cuss multiple definition.
            self.cuss_list[22].demand = True
            self.sym_cuss(self.cuss_list[22], symbol.name)

        if symbol.health == 5:
            # Indefinably leftover.
            self.cuss_list[30].demand = True
            self.sym_cuss(self.cuss_list[30], symbol.name)

        elif symbol.health == 7:
            # Multiple definition.
            self.cuss_list[22].demand = True
            self.sym_cuss(self.cuss_list[22], symbol.name)

        elif symbol.health in (8, 0xB):
            # Oversize location.
            self.cuss_list[20].demand = True
            self.sym_cuss(self.cuss_list[20], symbol.name)

        elif symbol.health in (9, 0xC):
            # Memory type error.
            self.cuss_list[16].demand = True
            self.sym_cuss(self.cuss_list[16], symbol.name)

        elif symbol.health in (0xA, 0xD):
            # Conflict of location contents.
            self.cuss_list[18].demand = True
            self.sym_cuss(self.cuss_list[18], symbol.name)

        elif symbol.health == 0xE:
            # Multiple errors.
            self.cuss_list[24].demand = True
            # Inhibit mult. def. cuss for healths E,F.
            self.cuss_list[22].demand = False
            self.sym_cuss(self.cuss_list[24], symbol.name)

        elif symbol.health == 0xE:
            # Miscellaneous trouble.
            self.cuss_list[26].demand = True
            # Inhibit mult. def. cuss for healths E,F.
            self.cuss_list[22].demand = False
            self.sym_cuss(self.cuss_list[26], symbol.name)

        return self.no_loc_sym(popo, symbol, print_line)

    def fits_fitz(self, popo):
        sym_addr = (popo.health >> 16) & 0xFFFF
        if sym_addr == 0:
            return None

        sym_keys = list(self._yul.sym_thr.keys())
        return self._yul.sym_thr[sym_keys[sym_addr-1]]

    def proc_adr(self, popo):
        # Form subfields from address field.
        adr_wd = self.adr_field(popo)

        if self._field_cod[0] is None:
            # Cuss and exit on meaningless field.
            self.cuss_list[8].demand = True
            self._address = ONES
            return

        if self._field_cod[0] == 0:
            # Fake zero modifier when field is blank.
            adr_wd[1] = 0
        else:
            unsigned_mask = FieldCodBit.UNSIGNED | FieldCodBit.NUMERIC
            # Br if main part is not signed numeric, or if relative to leftover location.
            if (self._field_cod[0] & unsigned_mask != FieldCodBit.NUMERIC) or self._yul.switch & SwitchBit.LEFTOVER:
                # Branch if main part is symbolic.
                if self._field_cod[0] == FieldCodBit.SYMBOLIC:
                    sym_value = self.symbol_ad(popo, adr_wd)
                    if sym_value is None:
                        return
                    else:
                        adr_wd[0] = sym_value
                if self._field_cod[1] != 0:
                    adr_wd[0] += adr_wd[1]
                return self.minad_chk(popo, adr_wd)

            if self._field_cod[1] != 0:
                # Add two signed numeric parts.
                adr_wd[0] += adr_wd[1]

            # Modifier relative current location.
            adr_wd[1] = adr_wd[0]

        adr_wd[0] = self._location
        if adr_wd[0] == ONES:
            # Cuss and exit when location is bad.
            self.cuss_list[29].demand = True
            self._address = ONES
            return

        adr_wd[0] += adr_wd[1]
        return self.minad_chk(popo, adr_wd)

    def minad_chk(self, popo, adr_wd):
        # Branch if value not too negative or more than CAC3.
        if (adr_wd[0] < self._min_adres) or (adr_wd[0] >= 0x10000):
            # Cuss and exit when address value faulty.
            self.cus_list[10].demand = True
            self._address = ONES
            return

        # Normal exit.
        sign = -1 if adr_wd[0] < 0 else 1
        self._address = sign * (abs(adr_wd[0]) & 0xFFFF)

    def symbol_ad(self, popo, adr_wd):
        # Analyze history of symbol.
        sym_name = adr_wd[0].strip()
        symbol = self.anal_symb(sym_name)
        if symbol is None:
            # Cuss and exit when symbol dont fit.
            self.cuss_list[15].demand = True
            self.sym_cuss(cuss_list[15], sym_name) 
            return None

        return self.symb_fits(symbol)

    def symb_fits(self, symbol):
        # Branch if health of symbol is B or more.
        if symbol.health >= 0xB:
            self.cuss_list[23].demand = True
            self.sym_cuss(self.cuss_list[23], symbol.name)

        if symbol.health == 0:
            # Undefined.
            self.cuss_list[9].demand = True
            self.sym_cuss(self.cuss_list[9], symbol.name)
            self._address = ONES
            return None

        elif symbol.health == 1:
            # Nearly defined by equals.
            self.cuss_list[47].demand = True
            self.sym_cuss(self.cuss_list[47], symbol.name)
            self._address = ONES
            return None

        elif symbol.health == 2:
            # Multiply defined including nearly by =.
            self.cuss_list[48].demand = True
            self.sym_cuss(self.cuss_list[48], symbol.name)
            self._address = ONES
            return None

        elif symbol.health in (3, 6):
            # Defined by equals or defined (no cuss).
            return symbol.value

        elif symbol.health == 4:
            # Multiply defined including by equals.
            self.cuss_list[50].demand = True
            self.sym_cuss(self.cuss_list[50], symbol.name)
            return symbol.value

        elif symbol.health == 5:
            # Failed leftover.
            self.cuss_list[49].demand = True
            self.sym_cuss(self.cuss_list[49], symbol.name)
            self._address = ONES
            return None

        elif symbol.health == 7:
            # Multiply defined.
            self.cuss_list[23].demand = True
            self.sym_cuss(self.cuss_list[23], symbol.name)
            return symbol.value

        elif symbol.health in (8, 0xB):
            # Oversize definition.
            self.cuss_list[21].demand = True
            self.sym_cuss(self.cuss_list[21], symbol.name)
            self._address = ONES
            return None

        elif symbol.health in (9, 0xC):
            # Wrong memory type.
            self.cuss_list[17].demand = True
            self.sym_cuss(self.cuss_list[17], symbol.name)
            return symbol.value

        elif symbol.health in (0xA, 0xD):
            # Conflict.
            self.cuss_list[19].demand = True
            self.sym_cuss(self.cuss_list[19], symbol.name)
            return symbol.value

        elif symbol.health == 0xE:
            # Multiple errors.
            self.cuss_list[25].demand = True
            # No multiple definition cuss for E and F.
            self.cuss_list[23].demand = False
            self.sym_cuss(self.cuss_list[25], symbol.name)
            return None

        else: # 0xF
            # Miscellaneous trouble.
            self.cuss_list[27].demand = True
            # No multiple definition cuss for E and F.
            self.cuss_list[23].demand = False
            self.sym_cuss(self.cuss_list[27], symbol.name)
            return None

    # Procedure in pass 2 for SETLOC. Does not accept any changes in the status of an
    # address symbol.
    def setloc(self, popo):
        # Maybe cuss  D  error.
        if popo.health & Bit.BIT9:
            self.cuss_list[1].demand = True

        # Maybe cuss nonblank loc field.
        if popo.health & Bit.BIT8:
            self.cuss_list[43].demand = True

        # Maybe cuss wrong memory type.
        if popo.health & Bit.BIT10:
            self.cuss_list[5].demand = True

        # Maybe cuss meaningless address field.
        if popo.health & Bit.BIT13:
            self.cuss_list[8].demand = True

        # Maybe cuss address size error.
        if popo.health & Bit.BIT14:
            self.cuss_list[10].demand = True

        # Branch if adr sym fitted in sym tab.
        if popo.health & Bit.BIT16:
            adr_wd = self.adr_field(popo)
            if len(symbol) < 8:
                # Get address symbol (headed).
                symbol = ('%-7s%s' % (adr_wd[0], self._head)).strip()
            self.sym_cuss(self.cuss_list[15], symbol)
            self.cuss_list[15].demand = True
            return self.form_locn(good_loc=False)

        adr_symbol = self.fits_fitz(popo)
        # Branch if no address symbol.
        if adr_symbol is None:
            return self.form_locn(popo)

        if popo.health & Bit.BIT11:
            # Undefined setloc symbol is fatal.
            self.sym_cuss(self.cuss_list[44], adr_symbol.name)
            # Cuss no define by pass 1.
            self.cuss_list[44].demand = True

        if popo.health & Bit.BIT12:
            self.sym_cuss(self.cuss_list[45], adr_symbol.name)
            # Cuss near define by pass 1.
            self.cuss_list[45].demand = True

        # Modify and visit address symbol cusser.
        self.symb_fits(adr_symbol)

        # Branch if no definition from pass 1.
        if (popo.health & (Bit.BIT11 | Bit.BIT12)) != 0:
            return self.form_locn(popo, good_loc=False)

        # Branch if no address field problems.
        if (popo.health & (Bit.BIT13 | Bit.BIT14)) == 0:
            return self.form_locn(popo)

        return self.form_locn(popo, good_loc=False)

    def form_locn(self, popo, good_loc=True):
        if good_loc:
            # Use determined location
            location = popo.health & 0xFFFF
        else:
            # Signal bad location
            location = ONES

        # Print loc value if any.
        self.m_ploc_is(location)
        self.print_lin()
        return self.pag_loxim(popo)

    def erase(self, popo):
        # Maybe cuss  D  error.
        if popo.health & Bit.BIT9:
            self.cuss_list[1].demand = True

        # Maybe cuss predefinition failure.
        if popo.health & Bit.BIT10:
            self.cuss_list[13].demand = True

        # Maybe cuss meaningless address field.
        if popo.health & Bit.BIT11:
            self.cuss_list[8].demand = True

        # Maybe cuss address size error.
        if popo.health & Bit.BIT12:
            self.cuss_list[10].demand = True

        # Maybe cuss type error.
        if popo.health & Bit.BIT13:
            self.cuss_list[5].demand = True

        # Branch if location is symbolic.
        if popo.health & Bit.BIT8:
            # Mabye cuss loc sym no fit in table.
            if popo.health & Bit.BIT16:
                self.cuss_list[14].demand = True
            # Analyze and pre-process location symbol.
            loc_symbol = self.loc_sym_1(popo)
        else:
            # Proclaim abscense of location symbol.
            loc_symbol = None

        no_eraloc = False

        # Branch if erase is leftover.
        if popo.health & Bit.BIT15:
            # Branch if there is a location symbol.
            if not popo.health & Bit.BIT8:
                self.cuss_list[46].demand = True
            # Branch if leftover is now defined.
            elif loc_symbol.defined:
                # Use location value found by pass 1.5 to
                # form upper and lower erase addresses.
                popo.health |= (symbol.value & 0xFFFF) << 16
                upper_addr = (popo.health & 0xFFFF) + symbol.value
                popo.health &= ~0xFFFF
                popo.health |= upper_addr
            else:
                no_eraloc = True
        else:
            # Maybe cuss location conflict.
            if popo.health & Bit.BIT14:
                self.cuss_list[4].demand = True

            if not popo.health & Bit.BIT8:
                # Maybe cuss unsigned numeric loc
                if popo.health & Bit.BIT16:
                    self.cuss_list[52].demand = True
                if popo.health & Bit.BIT17:
                    no_eraloc = True

            if (popo.health & (Bit.BIT11 | Bit.BIT12)) != 0:
                no_eraloc = True

        if no_eraloc:
            # Show that there is no location value.
            location = ONES
        else:
            location = (popo.health >> 16) & 0xFFFF

        # Print or blot first location.
        self.m_ploc_eb(location)

        # Branch if there is no location value.
        if location != ONES:
            location = popo.health & 0xFFFF

        # Print or blot second location.
        self.m_ploc_is(location)

        # Quick exit if no symbol.
        if loc_symbol is None:
            return self.no_loc_sym(popo)

        # Call for location symbol cussing.
        return self.health_cq(popo, loc_symbol)

    def _2octal(self, popo):
        pass

    def _2decimal(self, popo):
        pass

    def block(self, popo):
        pass

    def head_tail(self, popo):
        pass

    def too_late(self, popo):
        pass

    def subro(self, popo):
        pass

    def instruct_p1(self, popo):
        pass

    def even(self, popo):
        pass

    def count(self, popo):
        pass

    def segnum(self, popo):
        pass

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
                _, value = self.anal_subf(afield[16:], popo, check_blank=False)

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
                _, value = self.anal_subf(afield[16:], popo, check_blank=False)

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

    def anal_subf(self, common, popo, check_blank=True):
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
                    # Set complaint when 8s or 9s and no D.
                    if not self._field_cod[0] & FieldCodBit.DECIMAL:
                        popo.health |= Bit.BIT9
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

    # Subroutine in pass 2 to analyze and pre-process a location symbol.
    def loc_sym_1(self, popo):
        # Fetch location field of card.
        common = popo.loc_field().strip()

        # Branch if location symbol is in table.
        if self.cuss_list[14].demand:
            # Cuss fit failure and exit.
            self.sym_cuss(self.cuss_list[14], common)
            return None

        # Get history of normalized symbol.
        symbol = self.anal_symb(common)

        # Show whether there is a valid definition.
        symbol.defined = (((self._def_xform << 1) >> symbol.health) & 0x1) == 1

        return symbol

    def anal_symb(self, symbol):
        if len(symbol) < 8:
            symbol = ('%-7s%s' % (symbol, self._head)).strip()
        if symbol not in self._yul.sym_thr:
            self._yul.sym_thr[symbol] = Symbol(symbol)
        return self._yul.sym_thr[symbol]

    def sym_cuss(self, cuss, common):
        cuss.msg = cuss.msg[0] + ('%-8s' % common) + cuss.msg[9:]

    def send_sypt(self, card):
        pass

    def cusser(self):
        line_cussed = False
        left_end = 0

        for cuss in self.cuss_list:
            if cuss.demand:
                cuss.demand = False
                line_cussed = True
                left_end = self.prin_cuss(cuss)

        if line_cussed:
            self.count_cus(left_end, 9)

    def prin_cuss(self, cuss):
        left_end = (16 + len(cuss.msg)) // 8
        self._line.text = self._line.text[:16] + cuss.msg + self._line.text[left_end*8:]
        # FIXME: If 1st cuss of page, left end of blots.

        # Poison indicates fatal cuss (bad assy).
        if cuss.poison:
            # Effect conditional suppression.
            self._yul.switch |= SwitchBit.SUPPRESS_INACTIVE
            # Indicate that assembly is bad.
            self._yul.switch |= SwitchBit.BAD_ASSEMBLY

        self.numb_cuss()

        return left_end

    def numb_cuss(self):
        # Form serial number for this cussed line.
        cuss_no = self._n_err_lins + 1
        self._line.text = 'E■■■■■■ ' + self._line.text[8:]

        # Print serial "# NN  " and text of cuss.
        serial_text = '# %d' % cuss_no
        self._line.text = self._line.text[:8] + serial_text + self._line.text[8+len(serial_text):]
        self.print_lin()

    def count_cus(self, left_end, right_end):
        self._n_err_lins += 1
        if self._err_pages[0] is None:
            # On first error, save page number.
            self._err_pages[0] = self._yul.page_head[-4:]

        # Branch if cussed line is first on page.
        elif self._err_pages[1] != self._yul.page_head[-4:]:
            prev_cuss = 'PRECEDING CUSSED LINE IS ON PAGE%s ■■■' % self._err_pages[1]
            # Fill empty part of 1st cuss with blots.
            blot_words = '■■■■■■■■' * (right_end - left_end)
            end_idx = left_end*8 + len(blot_words) + len(prev_cuss)
            self._old_line.text = self._old_line.text[:left_end*8] + blot_words + prev_cuss + self._old_line.text[end_idx:]

        # Show latest page number with error.
        self._err_pages[1] = self._yul.page_head[-4:]

    def print_lin(self):
        # New line ages suddenly.
        old_line = self._old_line
        self._old_line = self._line

        if self._line.text[0] == 'L':
            if self._line.spacing <= 1:
                # Change log card SP1 to SP2.
                self._line.spacing = 2

            # Erase any special flag at end of loglin.
            self._user_log.text = self._user_log.text[:116] + ' '*4

            # Lose any right print on log card.
            self._yul.switch &= ~SwitchBit.LAST_REM

            # Always start page number at 1.
            self._user_log.text = self._user_log.text[:100] + '   1' + self._user_log.text[104:]

            # Keep log line for page subheads.
            self._user_log.text = self._line.text[:80] + self._user_log.text[80:]

            # Set up "USER'S OWN PAGE NO."
            self._user_page = 1
            self._line.text = self._line.text[:80] + self._user_log.text[80:]

            # Branch unless printing is suppressed.
            if self._yul.switch & SwitchBit.PRINT:
                return self.prin_skip(old_line)

            # Exit at once if page head is owed.
            if self._yul.switch & SwitchBit.OWE_HEADS:
                return self.print_old()

            # Print E and owe heads if E is owed.
            if old_line.text[0] == 'E':
                self._yul.switch |= SwitchBit.OWE_HEADS
                return self.endoform(old_line, False)

            # If nothing is owed, we're in mid-page. So print blank line(s) to
            # get to E-O-F.
            self._yul.switch |= SwitchBit.OWE_HEADS
            return self.endoform(old_line, True)

        # Make card number look helpful by suppressing at most two zeros.
        # From right to left (columns 7 and 6).
        if self._line.text[6] == '0':
            self._line.text = self._line.text[:6] + ' ' + self._line.text[7:]
            if self._line.text[5] == '0':
                self._line.text = self._line.text[:5] + ' ' + self._line.text[6:]

        # Branch unless printing is suppressed.
        if not self._yul.switch & SwitchBit.PRINT:
            # Branch unless owe a cuss or cussed line.
            if self._line.text[0] == 'E':
                # Single-space any line preceding E-line.
                old_line.spacing = 1
                self._line.spacing = 2

                # Branch if we owe heads.
                if self._yul.switch & SwitchBit.OWE_HEADS:
                    return self.page_unit(old_line)

                self._yul.switch &= ~SwitchBit.OWE_HEADS

                # Add to line count from last line.
                self._lin_count += old_line.spacing & ~Bit.BIT1
                return self.print_old(old_line)

            # Exit at once if nor this nor last was E.
            if old_line.text[0] != 'E':
                return self.print_old()

            # Add to line count from last line.
            self._lin_count += old_line.spacing & ~Bit.BIT1

            # Back to normal print.
            if self._lin_count <= self._yul.n_lines:
                return self.print_old(old_line)

            self._yul.switch |= SwitchBit.OWE_HEADS
            return self.endoform(old_line, False)

        # Unless immediately following a log card, skip to head of form before ..P.. card.
        if self._line.text[0] == 'P' and old_line.text[0] != 'L':
            return self.prin_skip(old_line)

        # Branch unless A-line after C-line.
        if self._line.text[0] == 'A':
            if old_line.text[0] != 'C':
                return self.ask_skip(old_line)

            # Maybe copy 2nd loc and word of DP const.
            self._line.text = self._line.text[:8] + old_line.text[8:48] + self._line.text[48:]

            # Absorb it into A-line if it was.
            if not self._line.text[40:48].isspace():
                return self.print_old()

        # Branch if not pass 2 error/warning line or continuation line.
        if not self._line.text[0] in 'EC':
            return self.ask_skip(old_line)

        if self._lin_count != self._yul.n_lines:
            # Keep "E" and "C" lines on same page.
            self._lin_count -= 1

        # Branch if last line is already skip.
        if old_line.spacing & Bit.BIT1:
            # Move last lines skip to this E-line.
            self._line.spacing = Bit.BIT1

        # Branch if last line is SP1.
        elif old_line.spacing <= 1:
            # Make last line SP1.
            old_line.spacing = 1

        else:
            # If not, space this line 1 less.
            self._line.spacing = old_line.spacing - 1

        # Make last line SP1.
        old_line.spacing = 1
        return self.ask_skip(old_line, False)

    def ask_skip(self, old_line, check_skip=True):
        # Branch if last line is skip.
        if check_skip and old_line.spacing & Bit.BIT1:
            return self.prin_skip(old_line)

        # Add to line count from last line.
        self._lin_count += old_line.spacing

        # Branch to normal print.
        if self._lin_count <= self._yul.n_lines:
            return self.print_old(old_line)

        return self.prin_skip(old_line)

    def prin_skip(self, old_line, check_cusses=True):
        # "Branch" if any cusses on this page.
        if check_cusses and not self._yul.switch & SwitchBit.CUSSES_ON_PAGE:
            # Skip after last line at end of page.
            old_line.spacing = Bit.BIT1
            return self.dpaginat(old_line)

        # Set up SP2 and record it in line count.
        old_line.spacing = 2
        self._lin_count += old_line.spacing

        # Branch if more copies should be done.
        if self._yul.n_copies > 0:
            self.copy_prt5()

        self._mon.phi_print(old_line.text, old_line.spacing)

        # Turn off cusses-on-this-page flag.
        self._yul.switch &= ~SwitchBit.CUSSES_ON_PAGE

        # Branch if not yet at end of form.
        if self._lin_count <= self._yul.n_lines:
            # Go to end of form by blank lines w/ SP2.
            old_line.text = ' '*120
            return self.prin_skip(old_line, check_cusses=False)

        # Prepare a wham for last line of page.
        old_line.spacing = Bit.BIT1
        old_line.text = '■'*120
        return self.dpaginat(old_line)

    def dpaginat(self, old_line):
        # FIXME: what does DEPAGIN8 do?
        # if self._yul.n_copies > 0:
        #     self.copy_prt5()
        #self._mon.phi_print('', spacing=Bit.BIT1)

        if self._yul.n_copies > 0:
            self.copy_prt5()

        self._mon.phi_print(old_line.text, spacing=old_line.spacing)

        return self.page_unit(old_line)

    # Printing of page head and subhead (loc), and detail lines.

    def page_unit(self, old_line):
        self._page_no += 1
        # Put page number alpha in page head.
        self._yul.page_head = self._yul.page_head[:116] + ('%4d' % self._page_no)

        return self.print_hed(old_line)

    def print_hed(self, old_line):
        if self._yul.n_copies > 0:
            self.copy_prt5()
        self._mon.phi_print(self._yul.page_head, spacing=3)
        # Reset line count to 3.
        self._lin_count = 3

        # Finish up and exit if no log.
        if self._user_page > 0:
            # Go to print if not new log.
            if self._user_page != 1:
                # Put page no. in alpha in page subhead.
                self._user_log.text = self._user_log.text[:100] + ('%4d' % self._user_page) + self._user_log.text[104:]

            # Print log line now if heads are owed.
            elif not self._yul.switch & SwitchBit.OWE_HEADS:
                # Advance page no. for next use of log.
                self._user_page = 2
                return self.print_old()

            if self._yul.n_copies > 0:
                self.copy_prt5()

            # Print log line and double space.
            self._mon.phi_print(self._user_log.text, spacing=self._user_log.spacing)
            self._user_page += 1

            # Accordingly set line count to 5.
            self._lin_count += self._user_log.spacing

        # Exit now unless heads were owed.
        if not self._yul.switch & SwitchBit.OWE_HEADS:
            return self.print_old()

        # Now heads are paid up, print a cussed L.
        self._yul.switch &= ~SwitchBit.OWE_HEADS

        # Add to line count from last line.
        self._lin_count += old_line.spacing & ~Bit.BIT1
        return self.print_old(old_line)

    def endoform(self, old_line, check_cusses):
        if check_cusses and not self._yul.switch & SwitchBit.CUSSES_ON_PAGE:
            # Branch if more copies should be done.
            if self._yul.n_copies > 0:
                self.copy_prt5()

            # FIXME: DEPAGIN8

            # Print last line, skip, and owe heads.
            old_line.spacing = Bit.BIT1
            return self.print_old(old_line)

        self._yul.switch &= ~SwitchBit.CUSSES_ON_PAGE

        # Set up SP2 and record it in line count.
        old_line.spacing = 2
        self._lin_count += old_line.spacing

        if self._yul.n_copies > 0:
            self.copy_prt5()

        self.phi_print(old_line.text, old_line.spacing)

        if self._lin_count <= self._yul.n_lines:
            old_line.text = ' '*120
            return self.endoform(old_line, False)

    def print_old(self, old_line=None):
        if old_line is not None:
            if self._yul.n_copies != 0:
                self.copy_prt5()

            self._mon.phi_print(old_line.text, old_line.spacing)

        # Old line discovers fountain of youth. And moreover is made clean again.
        self._line = Line()

    def copy_prt5(self):
        pass

    def pass_1p5(self):
        # print('\nSYMBOL TABLE:')
        # print('-------------')
        # syms = sorted(self._yul.sym_thr.keys(), key=lambda sym: [ALPHABET.index(c) for c in sym])
        # for sym in syms:
        #     s = self._yul.sym_thr[sym]
        #     print('%-8s: %04o (%x)' % (sym, s.value, s.health))
        #     if s.definer is not None:
        #         print('  - Defined by: %s' % s.definer)
        #     if len(s.definees) > 0:
        #         print('  - Defines:    %s' % ', '.join(s.definees))

        # FIXME: resolve leftovers

        self.resolvem()
        self.assy_typ_q()

    def resolvem(self):
        for sym_name, symbol in self._yul.sym_thr.items():
            # If not nearly defined, seek another.
            if symbol.health > 0x0 and symbol.health < 0x3:
                self.def_test(symbol)

    def def_test(self, symbol):
        # Mark definer thread.
        symbol.analyzer = 1

        # Fetch symbol health code.
        definer = self._yul.sym_thr[symbol.definer]
        # "Branch" if symbol has no valid defin.
        undefined = (self._def_xform >> (16 + definer.health)) & 0x1

        if not undefined:
            # Fetch first-definee thread, go define.
            self.definem(definer)
        elif definer.analyzer:
            # Vicious circle if marked.
            self.voidem(definer)
        elif definer.health > 0x0 and definer.health < 0x3:
            # Continue definer search.
            self.def_test(definer)
        else:
            # Branch if symbol is undefinable.
            self.voidem(definer)

    def voidem(self, definer):
        # Void a definer thread.
        definer.analyzer = 2
        for definee in definer.definees:
            def_symbol = self._yul.sym_thr[definee]

            if def_symbol.analyzer != 2:
                self.voidem(def_symbol)

    def definem(self, definer):
        for definee in definer.definees:
            def_symbol = self._yul.sym_thr[definee]

            # Reconstitute signed modifier.
            def_symbol.value += definer.value
            if def_symbol.value < 0 or def_symbol.value > self.adr_limit:
                if def_symbol.health == 0x1:
                    # Nearly def becomes oversize defined.
                    def_symbol.health = 0x8
                else:
                    # Mult near def becomes mult oversize def.
                    def_symbol.health = 0xB
            else:
                if def_symbol.health == 0x1:
                    # Nearly defined becomes defined by =.
                    def_symbol.health = 0x3
                else:
                    # Mult nearly def becomes mult def by =.
                    def_symbol.health = 0x4

            self.definem(def_symbol)

    def assy_typ_q(self):
        if not self._yul.switch & SwitchBit.REPRINT:
            return self.real_assy()

        # FIXME: handle revisions and bad merges

    # Assembly of a new program or subroutine, or a well-merged revision or version. Clean out the
    # delete list and refurbish the lists of threads to subsidiary subroutines.
    def real_assy(self):
        # FIXME: handle deletes?
        # FIXME: create files, update metadata
        return self.inish_p2()

    # Initializing procedure for pass 2.
    def inish_p2(self):
        # Turn on print switch for main part.
        self._yul.switch |= SwitchBit.PRINT

        # Initialize count of word records.
        self._n_word_recs = 0
        self._yul.switch &= ~SwitchBit.LAST_REM

        self._err_pages = [None, None]

        return self.pass_2()

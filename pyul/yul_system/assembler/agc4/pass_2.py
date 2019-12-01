from yul_system.types import ONES, BAD_WORD, Bit, SwitchBit
from yul_system.assembler.pass_2 import Pass2, Cuss

class AGC4Pass2(Pass2):
    def __init__(self, mon, yul, adr_limit, m_typ_tab):
        super().__init__(mon, yul, adr_limit, m_typ_tab)

        self.d1_params = [16383.0, 16384.0, 16383]
        self.k1_maxnum = 0o77777
        self.d2_params = [268435455.0, 268435456.0, 268435455]
        self.k2_maxnum = 0o7777777777
        self.con_mask = [39, 44]

        self._max_adres = 0

        self._implads = [
                0,
                1,
                2,
                14,
                15,
                21,
                3071
        ]

        self.cuss_list = [
            # 0-2
            Cuss('CARD NUMBER OUT OF SEQUENCE     '),
            Cuss('NO "D" IN DECIMAL SUBFIELD      '),
            Cuss('ILLEGAL OR MIS-SPELLED OPERATION CODE   ', poison=True),

            # 3-5
            Cuss('IMPROPER LEFTOVER LOCATION FIELD FORMAT ', poison=True),
            Cuss('CONFLICT IN USE OF THIS LOCATION', poison=True),
            Cuss('LOCATION IS IN WRONG MEMORY TYPE', poison=True),

            # 6-8
            Cuss('OVERSIZE OR ILL-DEFINED LOCATION', poison=True),
            Cuss('ILLEGAL POLISH INDEXING ', poison=True),
            Cuss('ADDRESS FIELD IS MEANINGLESS    ', poison=True),

            # 9-11
            Cuss('"        " IS UNDEFINED ', poison=True),
            Cuss('RANGE ERROR IN VALUE OF ADDRESS ', poison=True),
            Cuss('IRREGULAR BUT ACCEPTABLE ADDRESS'),

            # 12-14
            Cuss('LEFTOVER WON\'T FIT IN MEMORY    ', poison=True),
            Cuss('ATTEMPT TO PREDEFINE LOCATION SYMBOL FAILED     ', poison=True),
            Cuss('"        " WON\'T FIT IN SYMBOL TABLE    ', poison=True),

            # 15-17
            Cuss('"        " WON\'T FIT IN SYMBOL TABLE    ', poison=True),
            Cuss('"        " ASSOCIATED WITH WRONG MEMORY TYPE    ', poison=True),
            Cuss('"        " ASSOCIATED WITH WRONG MEMORY TYPE    ', poison=True),

            # 18-20
            Cuss('"        " ASSOCIATED WITH CONFLICT     ', poison=True),
            Cuss('"        " ASSOCIATED WITH CONFLICT     ', poison=True),
            Cuss('"        " GIVEN OVERSIZE DEFINITION    ', poison=True),

            # 21-23
            Cuss('"        " GIVEN OVERSIZE DEFINITION    ', poison=True),
            Cuss('"        " GIVEN MULTIPLE DEFINITIONS   ', poison=True),
            Cuss('"        " GIVEN MULTIPLE DEFINITIONS   ', poison=True),

            # 24-26
            Cuss('"        " ASSOCIATED WITH MULTIPLE ERRORS      ', poison=True),
            Cuss('"        " ASSOCIATED WITH MULTIPLE ERRORS      ', poison=True),
            Cuss('"        " IS IN MISCELLANEOUS TROUBLE  ', poison=True),

            # 27-29
            Cuss('"        " IS IN MISCELLANEOUS TROUBLE  ', poison=True),
            Cuss('"        " WAS NEARLY DEFINED BY EQUALS ', poison=True),
            Cuss('ADDRESS DEPENDS ON UNKNOWN LOCATION     ', poison=True),

            # 30-32
            Cuss('"        " IS INDEFINABLY LEFTOVER      ', poison=True),
            Cuss('"        " MULTIPLY DEFINED INCLUDING NEARLY BY EQUALS  ', poison=True),
            Cuss('"        " MULTIPLY DEFINED INCLUDING BY EQUALS ', poison=True),

            # 33-35
            Cuss('ADDRESS IS IN BANK 00   ', poison=True),
            Cuss('ADDRESS IS INAPPROPRIATE FOR OP CODE    '),
            Cuss('ADDRESS         '),

            # 36-38
            Cuss('THIS INSTRUCTION SHOULD BE INDEXED      '),
            Cuss('CCS CANNOT REFER TO FIXED MEMORY'),
            Cuss('INEXACT DECIMAL-TO-BINARY CONVERSION    '),

            # 39-41
            Cuss('MORE THAN 10 DIGITS IN DECIMAL CONSTANT '),
            Cuss('RANGE ERROR IN CONSTANT FIELD   ', poison=True),
            Cuss('FRACTIONAL PART LOST BY TRUNCATION      '),

            # 42-44
            Cuss('MORE THAN 14 DIGITS IN OCTAL CONSTANT   '),
            Cuss('LOCATION FIELD SHOULD BE BLANK  '),
            Cuss('"        " WAS UNDEFINED IN PASS 1      ', poison=True),

            # 45-47
            Cuss('"        " WAS NEARLY DEFINED BY EQUALS IN PASS 1       ', poison=True),
            Cuss('LOCATION FIELD SHOULD BE SYMBOLIC       ', poison=True),
            Cuss('"        " WAS NEARLY DEFINED BY EQUALS ', poison=True),

            # 48-50
            Cuss('"        " MULTIPLY DEFINED INCLUDING NEARLY BY EQUALS  ', poison=True),
            Cuss('"        " IS INDEFINABLY LEFTOVER      ', poison=True),
            Cuss('"        " MULTIPLY DEFINED INCLUDING BY EQUALS ', poison=True),

            # 51-53
            Cuss('"        " SHOULDN\'T HAVE BEEN PREDEFINED       ', poison=True),
            Cuss('NUMERIC LOCATION FIELD IS ILLEGAL HERE  ', poison=True),
            Cuss('NO SUCH BANK IN THIS MACHINE    ', poison=True),

            # 54-56
            Cuss('THIS BANK IS FULL       ', poison=True),
            Cuss('ILLEGAL LOCATION FIELD FORMAT   ', poison=True),
            Cuss('CARD IGNORED BECAUSE IT\'S TOO LATE IN THE DECK  ', poison=True),

            # 57-59
            Cuss('CARD IGNORED BECAUSE IT MAKES MEMORY TABLE TOO LONG     ', poison=True),
            Cuss('NO MATCH FOUND FOR CARD NUMBER OR ACCEPTOR TEXT ', poison=True),
            Cuss('FIRST CARD NUMBER NOT LESS THAN SECOND  ', poison=True),

            # 60-62
            Cuss('QUEER INFORMATION IN COLUMN 1   '),
            Cuss('QUEER INFORMATION IN COLUMN 17  '),
            Cuss('QUEER INFORMATION IN COLUMN 24  '),

            # 63-65
            Cuss('BLANK ADDRESS FIELD EXPECTED    '),
            Cuss('ADDRESS FIELD SHOULD CONTAIN A POLISH OPERATOR  ', poison=True),
            Cuss('OVERFLOW IN POLISH OPERATOR WORD', poison=True),

            # 66-68
            Cuss('FIRST ADDRESS OF AN EQUATION MUST BE POSITIVE   ', poison=True),
            Cuss('FIRST POLISH OPERATOR ILLEGAL INDEXED   ', poison=True),
            Cuss('SECOND POLISH OPERATOR ILLEGAL INDEXED  ', poison=True),

            # 69-71
            Cuss('NO MATCH FOUND FOR SECOND CARD NUMBER   ', poison=True),
            Cuss('LAST OPERATOR WORD COUNT WRONG  ', poison=True),
            Cuss('THIS CODE MAY BECOME OBSOLETE   '),

            # 72-74
            Cuss(''),
            Cuss(''),
            Cuss(''),

            # 75-77
            Cuss(''),
            Cuss(''),
            Cuss(''),

            # 78-80
            Cuss(''),
            Cuss(''),
            Cuss(''),

            # 81-83
            Cuss(''),
            Cuss(''),
            Cuss(''),

            # 84-86
            Cuss(''),
            Cuss(''),
            Cuss(''),

            # 87-89
            Cuss(''),
            Cuss(''),
            Cuss(''),

            # 90-92
            Cuss('ASTERISK ILLEGAL ON THIS OP CODE', poison=True),
            Cuss(''),
            Cuss(''),

            # 93-95
            Cuss('SUBROUTINE NAME NOT RECOGNIZED  ', poison=True),
            Cuss('MULTIPLE CALLS IN ONE PROGRAM OR SUBRO  '),
            Cuss('CONFLICT WITH EARLIER HEAD SPECIFICATION', poison=True),
        ]

    # Subroutine in pass 2 for AGC4 to form a word from an operation code and an addess (basic instruction
    # and address constants), or from two polish operator codes (polish operator words). The operation code(s)
    # and some associated information bits are taken from the health word of the current POPO item. The address is
    # obtained from the card via a general subroutine in pass 2 called PROC ADR. Implied addresses, bank errors, and
    # inappropriate addresses are checked for, and address value cussing is done.
    def m_proc_op(self, popo):
        if popo.health & Bit.BIT32:
            return self.polish_op(popo)

        # Insert basic op code into word.
        self._word = (popo.health >> 12) & (Bit.BIT34 | Bit.BIT35 | Bit.BIT36)

        # Maybe cuss illegal op code asterisk.
        if popo.health & Bit.BIT11:
            self.cuss_list[90].demand = True

        # Branch if no implied address.
        if popo.health & Bit.BIT31:
            # Proceed if address field is blank.
            if not(popo.address_1().isspace() and popo.address_2().isspace()):
                # Otherwise cuss mildly and proceed.
                self.cuss_list[63].demand = True

            # Supply implied address.
            impl_idx = (popo.health >> 18) & 0xF
            self._address = self._implads[impl_idx]

            # Branch unless op code is "SQUARE".
            if popo.health & Bit.BIT25:
                # Br if extracode "SQUARE" is indexed.
                if self._yul.switch & SwitchBit.PREVIOUS_INDEX:
                    self.cuss_list[36].demand = True
            else:
                # Set current index bit for "EXTEND".
                self._yul.switch &= ~SwitchBit.CURRENT_INDEX
                self._yul.switch |= (popo.health >> 2) & SwitchBit.CURRENT_INDEX

                # Cuss indexing on non-extracode implads.
                if self._yul.switch & SwitchBit.PREVIOUS_INDEX:
                    self.cuss_list[7].demand = True

            # Clear false special condition flags.
            popo.health &= ~0o77000000
            return self.basic_sba(popo)

        # Branch if special condition is 5 or less, or 13 or more.
        spec_cond = (popo.health >> 19) & 0x1F
        if (spec_cond <= 5) or (spec_cond >= 0o13):
            # Branch to permit negative address.
            set_min = (self._word & (Bit.BIT34 | Bit.BIT35 | Bit.BIT36)) != Bit.BIT34
            return self.non_const(popo, set_min)

        dec6_flag = Bit.BIT2 | Bit.BIT3
        # Put constant flag on address constant.
        self._word |= dec6_flag

        # Branch if code = ADRES or CADR.
        if spec_cond <= 7:
            return self.non_const(popo, set_min=False)

        # Branch if code is not XCADR.
        if spec_cond > 0o11:
            # Set up 47777 in word and allow -address.
            self._word &= ~0o77777
            self._word |= 0o47777
            return self.non_const(popo)

        additive = 1

        # Go fish for ",1" or ",2"
        rite_norm = (popo.address_1() + popo.address_2()).rstrip()
        if len(rite_norm) >= 2 and rite_norm[-1] in '12' and rite_norm[-2] == ',':
            # Indicate indexing and remove comma.
            if rite_norm[-1] == '2':
                additive = 2
            additive |= Bit.BIT1
            rite_norm = rite_norm[:-2]
        else:
            additive = 1

        if spec_cond != 0o11:
            return self.polish_ad(popo, rite_norm, additive)

        # Add 32000 (direct) or 34000 (indexed)
        additive += 0o32000
        if additive & Bit.BIT1:
            additive += 0o2000

        # Set max, check op word count if needed
        self._max_adres = 0o1776
        return self.op_ck_stor(popo, rite_norm, additive)

    # Inactive address check and limit setup for polish addresses.
    def polish_ad(self, popo, rite_norm, additive):
        # Branch if no minus in col 17.
        if popo.card[16] == '-':
            # Cuss minus if first address of equation.
            if self._yul.switch & SwitchBit.BEGINNING_OF_EQU2:
                self.cuss_list[66].demand = True

            # Minimum magnitude is one if minus.
            self._min_adres = 1

        # Branch if not first address of equation.
        if self._yul.switch & SwitchBit.BEGINNING_OF_EQU2:
            # Branch if last operator word count ok.
            if self._op_count != 0:
                self.cuss_list[70].demand = True

            # Reset permission bit for minus polads.
            self._yul.switch &= ~SwitchBit.BEGINNING_OF_EQU2

        # Test for inactive address if unindexed.
        if additive <= Bit.BIT1:
            # Maximum value for polish unindexed.
            self._max_adres = 0o77776
            if rite_norm == '':
                # Polad w/ bl adr fld may be blank card.
                self.cuss_list[34].demand = True

            if rite_norm == '-':
                self._word |= 0o77777
                return self.gud_basic(popo)

            self._min_adres = -0o77777
            return self.max_ad_set(popo, rite_norm, additive)

        # Maximum augmenter for polish indexed.
        self._max_adres = 0o57776
        return self.pol_sign_t(popo, rite_norm, additive)

    def pol_sign_t(self, popo, rite_norm, additive):
        # Force range error if minus sign here.
        if popo.card[16] == '-':
            self._min_adres = 0o72000
        return self.max_ad_set(popo, rite_norm, additive)

    def op_ck_stor(self, popo, rite_norm, additive):
        # Exit if not beginning of equation.
        if self._yul.switch & SwitchBit.BEGINNING_OF_EQU2:
            if self._op_count > 0:
                # Cuss bad operator word count.
                self.cuss_list[70].demand = True

        self._yul.switch &= ~SwitchBit.BEGINNING_OF_EQU2
        return self.pol_sign_t(popo, rite_norm, additive)

    def non_const(self, popo, set_min=True):
        if set_min:
            self._min_adres = -0o7777
        self._max_adres = 0o71777

        return self.max_ad_set(popo, None, 0)

    def max_ad_set(self, popo, rite_norm, additive):
        # Translate address field.
        self.proc_adr(popo, rite_norm)

        # Restore min adr value.
        self._min_adres = 0

        # Cuss lack of "D" in decimal subfield.
        if popo.health & Bit.BIT9:
            self.cuss_list[1].demand = True

        if self._address >= ONES:
            # Meaningless or atrocious address.
            return self.bad_basic(popo)

        if self._address > self._max_adres:
            return self.rng_error(popo)

        # Branch if no constant flag.
        if self._word <= Bit.BIT17:
            return self.instrop(popo)

        # Branch if code is "ADRES".
        spec_cond = (popo.health >> 19) & 0x1F
        if spec_cond <= 6:
            return self.basic_sba(popo)

        # Use address as is for CADR.
        if spec_cond <= 7:
            self._word |= self._address & 0o77777
            return self.gud_basic(popo)

        # Branch if code is XCADR.
        if spec_cond >= 0o12:
            return self.basic_adr(popo)

        if not ((self._address <= 0o1777) or # Interpretive may address erasable ....
                ((additive >= Bit.BIT1) and (self._address <= 0o17777)) or # With some latitude if indexed....
                (self._address > 0o37777)): # ... or upper half of switched banks.
            return self.range_error(popo)

        # Use additive on polish or store address.
        self._word &= ~0o37777
        self._word |= (abs(self._address) + abs(additive)) & 0o37777

        if additive >= Bit.BIT1:
            # Use 2 x address if indexed.
            self._word += self._address

        # Branch if no minus sign in column 17.
        if popo.card[16] == '-':
            # Since interpreter does not ccs these.
            self._word -= 2

        return self.gud_basic(popo)
            

    def rng_error(self, popo):
        # Print bad-size address if possible.
        if self._address < 0o72000:
            self.cuss_list[35].demand = True
            self.prb_adres(self._address)
        # Cuss range error in address value.
        self.cuss_list[10].demand = True
        return self.bad_basic(popo)


    # Specific processing for basic instructions.
    def instrop(self, popo):
        # Branch if positive address value.
        if self._address < 0 and not self._yul.switch & SwitchBit.PREVIOUS_INDEX:
            # Cuss if no index before minus address.
            self.cuss_list[36].demand = True

        # Branch if there are no special conds.
        spec_cond = (popo.health >> 19) & 0x1F
        if spec_cond == 0:
           pass

        # CAF/OVIND
        elif spec_cond <= 2:
            # Warn of OVIND's coming obsolescence.
            if popo.health & Bit.BIT28:
                self.cuss_list[71].demand = True
            # No check on indexed caf or ovind.
            if not self._yul.switch & SwitchBit.PREVIOUS_INDEX:
                # Branch if value correct for CAF, OVIND.
                if self._address < 0o2000:
                    # Cuss inappropriate address.
                    self.cuss_list[34].demand = True
        # CCS
        elif spec_cond <= 3:
            # No check on indexed CCS.
            if not self._yul.switch & SwitchBit.PREVIOUS_INDEX:
                # Branch if value is correct for CCS.
                if self._address > 0o1777:
                    # Cuss CCS reference to fixed.
                    self.cuss_list[35].demand = True
                    self.prb_adres(self._address)
                    self.cuss_list[37].demand = True
        # INDEX
        elif spec_cond <= 4:
            # Set current index bit.
            self._yul.switch |= SwitchBit.CURRENT_INDEX
        # TS
        elif spec_cond <= 5:
            # Bypass check if instruction is indexed.
            if not self._yul.switch & SwitchBit.PREVIOUS_INDEX:
                if self._address > 0o1777:
                    # Fixed mem adres inappropriate for TS.
                    self.cuss_list[34].demand = True
        # XTRACODE
        else:
            if not self._yul.switch & SwitchBit.PREVIOUS_INDEX:
                # Cuss unindexed extracode.
                self.cuss_list[36].demand = True

        return self.basic_adr(popo)


    def basic_adr(self, popo):
        if self._address >= 0:
            return self.basic_sba(popo)

        # Add in negative address and go to print.
        return self.gud_basic(popo, adr_wd=self._address)

    def basic_sba(self, popo):
        # Branch if address not in a bank.
        adr_wd = self._address
        if self._address <= 0o5777:
            return self.gud_basic(popo, adr_wd=adr_wd)

        # Put subaddress in 6000-7777 class.
        adr_wd &= ~0o76000
        adr_wd |= 0o6000

        # Branch if location is not in a bank.
        if self._location <= 0o5777:
            return self.gud_basic(popo, adr_wd=adr_wd)

        # Branch on bank error.
        adr_bank = (self._address >> 10) & 0x1F
        loc_bank = (self._location >> 10) & 0x1F
        if adr_bank == loc_bank:
            # Go to assemble word.
            return self.gud_basic(popo, adr_wd=adr_wd)

        # Set poison bit of bank cuss = -indexed.
        cuss = self.cuss_list[33]
        cuss.poison = not self._yul.switch & SwitchBit.PREVIOUS_INDEX
        # Call for bank error cuss.
        cuss.demand = True
        # Insert bank number in bank cuss.
        cuss.msg = cuss.msg[:19] + ('%02o' % adr_bank) + cuss.msg[21:]
        return self.gud_basic(popo, adr_wd=adr_wd)

    # Printing procedures for basic instructions and address constants.

    def gud_basic(self, popo, adr_wd=0):
        # Put address or subaddress in word.
        self._word += adr_wd

        # Branch if no minus sign in column 17.
        if popo.card[16] == '-':
            # Complement negative instruction.
            self._word ^= 0o77777

        # Put basic code address into print image.
        self._line.text = self._line.text[:40] + ('%04o' % (self._word & 0o7777)) + self._line.text[44:]

        # Branch if word is an address constant.
        dec6_flag = Bit.BIT2 | Bit.BIT3
        first_digit = (self._word >> 12) & 0o7
        if self._word >= dec6_flag:
            # Print first digit of constant.
            self._line.text = self._line.text[:39] + ('%o' % first_digit) + self._line.text[40:]
        else:
            # Print op code of instruction.
            self._line.text = self._line.text[:38] + ('%o' % first_digit) + self._line.text[39:]
            # Branch on indexed instruction.
            if not self._yul.switch & SwitchBit.PREVIOUS_INDEX:
                # Mark as subject to bad reference code.
                dec48_flg = Bit.BIT2 | Bit.BIT5
                self._word |= dec48_flg

            # Supply bank indicator to simulator.
            bank_no = self._address >> 10
            self._word |= bank_no << 30
            # Store it twice to make parity OK.
            self._word |= bank_no << 24

            # Move current index bit to previous.
            self._yul.switch &= ~SwitchBit.PREVIOUS_INDEX
            if self._yul.switch & SwitchBit.CURRENT_INDEX:
                self._yul.switch |= SwitchBit.PREVIOUS_INDEX
            # Clear current index bit.
            self._yul.switch &= ~SwitchBit.CURRENT_INDEX

        return self.bc_check(popo)

    def bad_basic(self, popo):
        self._line.text = self._line.text[:40] + '■■■■' + self._line.text[44:]

        if self._word > Bit.BIT17:
            # Blot first digit of bad constant.
            self._line.text = self._line.text[:39] + '■' + self._line.text[40:]
        else:
            spec_cond = (popo.health >> 19) & 0x1F
            if spec_cond == 4:
                # Set previous index bit if index.
                self._yul.switch |= SwitchBit.PREVIOUS_INDEX
            else:
                # Clear previous index bit.
                self._yul.switch &= ~SwitchBit.PREVIOUS_INDEX
            # Branch if no minus sign in column 17.
            if popo.card[16] == '-':
                # Complement good op of bad neg. instr.
                self._word ^= 0o77777

            # Print good op code in bad instruction.
            first_digit = (self._word >> 12) & 0o7
            self._line.text = self._line.text[:38] + ('%o' % first_digit) + self._line.text[39:]

        self._word = BAD_WORD
        return self.bc_check(popo)

    def bc_check(self, popo):
        if popo.card[16] == '-':
            # Clear "should-be-indexed" cuss if minus.
            self.cuss_list[36].demand = False
        elif popo.card[16] != ' ':
            # Cuss if neither blank nor minus in CC 17.
            self.cuss_list[61].demand = True

        if popo.card[0] == 'J':
            # Clear "should-be-indexed" cuss if lftvr.
            self.cuss_list[36].demand = False
        elif popo.card[0] != ' ':
            # Cuss if neither blank nor J in column 1.
            self.cuss_list[60].demand = True

        # Cuss if column 24 non-blank.
        if popo.card[23] != ' ':
            self.cuss_list[62].demand = True

        # Return to general procedure.
        return

    def prb_adres(self, address):
        # Set up address of adr cuss.
        cuss = self.cuss_list[35]
        # Branch if address is in a bank.
        if address < 0o6000:
            # Move up non-bank address.
            cuss.msg = cuss.msg[:8] + ('=%04o  ' % address)
        else:
            bank_no = address >> 10
            # Put subaddress in the range 6000-7777.
            address = (address | 0o6000) & 0o7777
            cuss.msg = cuss.msg[:8] + ('=%02o,%04o' % (bank_no, address))

    def polish_op(self, popo):
        # Set up 7-bit left operator.
        self._word = (popo.health >> 17) & 0o37600

        # Revoke permission for minus addresses.
        self._yul.switch |= SwitchBit.BEGINNING_OF_EQU2
        
        # Branch on type of first operator.
        op_type = (popo.health >> 24) & 0x3
        if op_type == 0:
            # Move index bit to general operator.
            if popo.health & Bit.BIT11:
                self._word |= Bit.BIT40
        elif op_type == 1:
            # Cuss indexing of miscellaneous operator.
            if popo.health & Bit.BIT11:
                self.cuss_list[67].demand = True
        elif op_type == 3:
            # Move index bit to unary operator.
            if popo.health & Bit.BIT11:
                self._word |= Bit.BIT39

        # Branch unless second half is op word ct.
        sec_polop = (popo.health >> 17) & 0o177
        if sec_polop == 7:
            # Translate address field.
            self.proc_adr(popo)
            self._op_count = self._address

            # Maybe cuss "D" error.
            if popo.health & Bit.BIT9:
                self.cuss_list[1].demand = True

            # Branch if meaningless or atrocious adr.
            if self._address >= ONES:
                return self.two_poles(popo, bad=True)

            # Branch if count is 127 or less.
            if self._address <= 0o177:
                self._word |= self._address
                return self.sel_star_2(popo)

            # Branch if address is unprintable.
            if self._address < 0o72000:
                # Print oversize address.
                self.cuss_list[35].demand = True
                self.prb_adres(self._address)

            # Guarantee op count cuss.
            self._op_count = -1

            # Cuss range error in address value.
            self.cuss_list[10].demand = True
            return self.two_poles(popo, bad=True)

        # Branch if op count might still make it.
        if self._op_count != 0:
            self._op_count -= 1
        else:
            # Guarantee bad count if twas too small.
            self._op_count = -1

        if sec_polop == 0o17:
            # Cuss meaningless address field.
            self.cuss_list[8].demand = True
            return self.two_poles(popo, bad=True)

        if sec_polop == 0o27:
            # Cuss unpolish address field symbol.
            self.cuss_list[64].demand = True
            return self.two_poles(popo, bad=True)

        return self.two_poles(popo)

    # General processing of right operator.
    def two_poles(self, popo, bad=False):
        if bad:
            # Indicate badness of right operator.
            self._word |= Bit.BIT1

        # Set up 7-bit right operator.
        self._word |= ((popo.health >> 17) & 0o177)

        # Right-normalize address field and skip.
        addr = (popo.address_1() + popo.address_2()).rstrip()

        # Branch if operator 2 is not indexed.
        if len(addr) > 0 and addr[-1] == '*':
            # Branch on type of second operator
            sec_type = self._word & 3
            if sec_type == 0:
                # Apply index bit to general operator
                self._word |= 2
            elif sec_type == 1:
                # Cuss indexing of miscellaneous operator
                self.cuss_list[68].demand = True
            elif sec_type == 3:
                # Apply index bit to unary operator
                self._word |= 4

        return self.sel_star_2(popo)

    def sel_star_2(self, popo):
        # Add one and complement.
        word = ((self._word & 0o77777) + 1) ^ 0o77777
        self._word &= ~0o77777
        self._word |= word

        # Br if both ops = 177 (very queer).
        if word <= 0o37777:
            # Cuss overflow of operator word.
            self.cuss_list[65].demand = True
            
            # Set to plot out word like constant.
            self._word = Bit.BIT1
            return self.bad_basic(popo)

        # Complement word if "-" in col 17.
        if popo.card[16] == '-':
            self._word ^= 0o77777

        # Print left operator.
        self._line.text = self._line.text[:39] + ('%03o' % ((self._word >> 6) & 0o777)) + self._line.text[42:]

        # Branch if 2nd operator is bad.
        if self._word >= Bit.BIT1:
            # Blot out right operator, join main proc.
            self._line.text = self._line.text[:42] + '■■' + self._line.text[44:]
            self._word = BAD_WORD
            return self.bc_check(popo)

        # Print rest of operator word.
        self._line.text = self._line.text[:42] + ('%02o' % (self._word & 0o77)) + self._line.text[44:]

        # Plant flag of poland, join main proc.
        self._word |= (0x5 << 7*6)
        return self.bc_check(popo)

    # Subroutine in pass 2 for AGC4 to set in print a right-hand location for such as setloc.
    # Puts in the bank indicator, if any. Blots out an invalid location.
    def m_ploc_is(self, location):
        if location >= ONES:
            # Blot out bad location and exit.
            self._line.text = self._line.text[:42] + '■■■■' + self._line.text[46:]
            return

        # Branch if address is not in a bank.
        if location > 0o5777:
            # Set bank number in print.
            bank_no = location >> 10
            self._line.text = self._line.text[:39] + ('%02o,' % bank_no) + self._line.text[42:]
            # Put subaddress in the range 6000-7777.
            location = (location | 0o6000) & 0o7777

        # Set location in print and exit.
        self._line.text = self._line.text[:42] + ('%04o' % location) + self._line.text[46:]

    # Subroutine in pass 2 for AGC4 to set in print the location of an instruction or constant, with bank
    # number if any and with a notation for end of block or bank if required. Blots out location field if bad loc.
    def m_ploc_eb(self, location):
        if location >= ONES:
            self._line.text = self._line.text[:32] + '■■■■' + self._line.text[36:]
            return

        orig_loc = location

        # Branch if location is not in a bank.
        if location > 0o5777:
            # Set bank number in print.
            bank_no = location >> 10
            self._line.text = self._line.text[:29] + ('%02o,' % bank_no) + self._line.text[32:]

            # Put subaddress in the class 6000-7777.
            location = (location | 0o6000) & 0o7777

        if (location & 0o1777) == 0o1777:
            # Mark line "EB" for end of block or bank.
            self._line.text = self._line.text[:24] + '  EB' + self._line.text[28:]
        else:
            midx = 0
            # Branch when memory type category found.
            while orig_loc > self._m_typ_tab[midx][1]:
                midx += 1
            # Branch if not end of minor block.
            if orig_loc == self._m_typ_tab[midx][1]:
                # Mark line "MC" for memory type change.
                self._line.text = self._line.text[:24] + '  MC' + self._line.text[28:]

        # Set up location in print and exit.
        self._line.text = self._line.text[:32] + ('%04o' % location) + self._line.text[36:]

    # Subroutine in pass 2 for AGC4 to set up a single-precision constant in word and in print. This subroutine
    # does not care whether the word is signed or not, but demands the output of dec/oct const in number.
    def m_proc_1p(self, popo, number):
        if number == BAD_WORD:
            self._line.text = self._line.text[:39] + '■■■■■' + self._line.text[44:]
            self._word = number
            return

        # Isolate magnitude
        self._word = number & ~(Bit.BIT1)
        if not number & Bit.BIT1:
            # Complement negative word.
            self._word ^= 0o77777

        # Set word in print.
        self._line.text = self._line.text[:39] + ('%05o' % self._word) + self._line.text[44:]

        # Apply internal constant flag and exit
        dec6_flag = Bit.BIT2 | Bit.BIT3
        self._word |= dec6_flag

    # Subroutine in pass 2 for AGC4 to process a single-precision constant. Using the output of DEC CONST or
    # OCT CONST, and distinguishing between the signed and unsigned possibilities (for octal constants only),
    # sets up the high-order part in word and the low-order part in sec_half, sets the high-order part in print,
    # and sets up hte low-order part in printable form in sec_alf.
    def m_proc_2p(self, popo, number, e_number):
        # Branch if constant is valid.
        if number == BAD_WORD:
            # Prepare blots for low-order part.
            sec_alf = '■■■■■'
            self._line.text = self._line.text[:39] + '■■■■■' + self._line.text[44:]
            self._word = number
            return BAD_WORD, sec_alf

        # Branch if number is signed.
        if e_number != 0:
            # Set up unsigned constant.
            self._word = (number >> 14) & 0o37777
            common = 0o37777
        else:
            # Set up signed constant.
            self._word = (number >> 15) & 0o77777
            common = 0o77777

        # Isolate low-order part.
        sec_half = number & common

        # Branch if no minus sign.
        if not number & Bit.BIT1:
            # Complement halves of negative constant.
            self._word ^= 0o77777
            sec_half ^= 0o77777

        # Make printable version of low-order part
        sec_alf = '%05o' % sec_half

        # Set word in print.
        self._line.text = self._line.text[:39] + ('%05o' % self._word) + self._line.text[44:]

        # Apply internal constant flag and exit
        dec6_flag = Bit.BIT2 | Bit.BIT3
        self._word |= dec6_flag

        return sec_half, sec_alf

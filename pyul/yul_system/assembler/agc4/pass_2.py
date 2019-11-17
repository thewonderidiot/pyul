from yul_system.types import ONES, BAD_WORD, Bit, SwitchBit
from yul_system.assembler.pass_2 import Pass2, Cuss

class AGC4Pass2(Pass2):
    def __init__(self, mon, yul, adr_limit, m_typ_tab):
        super().__init__(mon, yul, adr_limit, m_typ_tab)
        
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
        if (spec_cond <= 5) or (spec_cond >= 13):
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
        if spec_cond > 11:
            # Set up 47777 in word and allow -address.
            self._word &= ~0o77777
            self._word |= 0o47777
            return self.non_const(popo)

        # FIXME: POL STORE


    def non_const(self, popo, set_min=True):
        if set_min:
            self._min_adres = -0o7777
        self._max_adres = 0o71777

        # Translate address field.
        self.proc_adr(popo)

        # Restore min adr value.
        self._min_adres = 0

        # Cuss lack of "D" in decimal subfield.
        if popo.health & Bit.BIT9:
            self.cuss_list[1].demand = True

        if self._address >= ONES:
            # Meaningless or atrocious address.
            return self.bad_basic(popo)

        if self._address > self._max_adres:
            # Print bad-size address if possible.
            if self._address < 0o72000:
                self.cuss_list[35].demand = True
                self.prb_adres(self._address)
            # Cuss range error in address value.
            self.cuss_list[10].demand = True
            return self.bad_basic(popo)

        # Branch if no constant flag.
        if self._word <= Bit.BIT17:
            return self.instrop(popo)

        # FIXME: CONSTANTS

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
        # FIXME

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
        pass

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

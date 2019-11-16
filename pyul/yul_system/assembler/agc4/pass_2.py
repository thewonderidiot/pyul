from yul_system.types import ONES
from yul_system.assembler.pass_2 import Pass2, Cuss

class AGC4Pass2(Pass2):
    def __init__(self, mon, yul, adr_limit, m_typ_tab):
        super().__init__(mon, yul, adr_limit, m_typ_tab)

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
            Cuss('ASTERISK ILLEGAL ON THIS OP CODE', poison=True),
            Cuss(''),
            Cuss(''),

            # 81-83
            Cuss('SUBROUTINE NAME NOT RECOGNIZED  ', poison=True),
            Cuss('MULTIPLE CALLS IN ONE PROGRAM OR SUBRO  '),
            Cuss('CONFLICT WITH EARLIER HEAD SPECIFICATION', poison=True),
        ]

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

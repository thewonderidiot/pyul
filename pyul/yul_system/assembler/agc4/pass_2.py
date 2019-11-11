from yul_system.assembler.pass_2 import Pass2, Cuss

class AGC4Pass2(Pass2):
    def __init__(self, mon, yul, adr_limit):
        super().__init__(mon, yul, adr_limit)

        self.cuss_list = [
            Cuss('CARD NUMBER OUT OF SEQUENCE'),
            Cuss('NO "D" IN DECIMAL SUBFIELD'),
            Cuss('ILLEGAL OR MIS-SPELLED OPERATION CODE', poison=True),

            Cuss('IMPROPER LEFTOVER LOCATION FIELD FORMAT', poison=True),
            Cuss('CONFLICT IN USE OF THIS LOCATION', poison=True),
            Cuss('LOCATION IS IN WRONG MEMORY TYPE', poison=True),

            Cuss('OVERSIZE OR ILL-DEFINED LOCATION', poison=True),
            Cuss('ILLEGAL POLISH INDEXING', poison=True),
            Cuss('ADDRESS FIELD IS MEANINGLESS', poison=True),

            Cuss('"        " IS UNDEFINED', poison=True),
            Cuss('RANGE ERROR IN VALUE OF ADDRESS', poison=True),
            Cuss('IRREGULAR BUT ACCEPTABLE ADDRESS'),

            Cuss('LEFTOVER WON\'T FIT IN MEMORY', poison=True),
            Cuss('ATTEMPT TO PREDEFINE LOCATION SYMBOL FAILED', poison=True),
            Cuss('"        " WON\'T FIT IN SYMBOL TABLE', poison=True),

            Cuss('"        " WON\'T FIT IN SYMBOL TABLE', poison=True),
            Cuss('"        " ASSOCIATED WITH WRONG MEMORY TYPE', poison=True),
            Cuss('"        " ASSOCIATED WITH WRONG MEMORY TYPE', poison=True),

            Cuss('"        " ASSOCIATED WITH CONFLICT', poison=True),
            Cuss('"        " ASSOCIATED WITH CONFLICT', poison=True),
            Cuss('"        " GIVEN OVERSIZE DEFINITION', poison=True),

            Cuss('"        " GIVEN OVERSIZE DEFINITION', poison=True),
            Cuss('"        " GIVEN MULTIPLE DEFINITIONS', poison=True),
            Cuss('"        " GIVEN MULTIPLE DEFINITIONS', poison=True),

            Cuss('"        " ASSOCIATED WITH MULTIPLE ERRORS', poison=True),
            Cuss('"        " ASSOCIATED WITH MULTIPLE ERRORS', poison=True),
            Cuss('"        " IS IN MISCELLANEOUS TROUBLE', poison=True),

            Cuss('"        " IS IN MISCELLANEOUS TROUBLE', poison=True),
            Cuss('"        " WAS NEARLY DEFINED BY EQUALS', poison=True),
            Cuss('ADDRESS DEPENDS ON UNKNOWN LOCATION', poison=True),

            Cuss('"        " IS INDEFINABLY LEFTOVER', poison=True),
            Cuss('"        " MULTIPLY DEFINED INCLUDING NEARLY BY EQUALS', poison=True),
            Cuss('"        " MULTIPLY DEFINED INCLUDING BY EQUALS', poison=True),

            Cuss('ADDRESS IS IN BANK 00', poison=True),
            Cuss('ADDRESS IS INAPPROPRIATE FOR OP CODE'),
            Cuss('ADDRESS'),

            Cuss('THIS INSTRUCTION SHOULD BE INDEXED'),
            Cuss('CCS CANNOT REFER TO FIXED MEMORY'),
            Cuss('INEXACT DECIMAL-TO-BINARY CONVERSION'),

            Cuss('MORE THAN 10 DIGITS IN DECIMAL CONSTANT'),
            Cuss('RANGE ERROR IN CONSTANT FIELD', poison=True),
            Cuss('FRACTIONAL PART LOST BY TRUNCATION'),

            Cuss('MORE THAN 14 DIGITS IN OCTAL CONSTANT'),
            Cuss('LOCATION FIELD SHOULD BE BLANK'),
            Cuss('"        " WAS UNDEFINED IN PASS 1', poison=True),

            Cuss('"        " WAS NEARLY DEFINED BY EQUALS IN PASS 1', poison=True),
            Cuss('LOCATION FIELD SHOULD BE SYMBOLIC', poison=True),
            Cuss('"        " WAS NEARLY DEFINED BY EQUALS', poison=True),

            Cuss('"        " MULTIPLY DEFINED INCLUDING NEARLY BY EQUALS', poison=True),
            Cuss('"        " IS INDEFINABLY LEFTOVER', poison=True),
            Cuss('"        " MULTIPLY DEFINED INCLUDING BY EQUALS', poison=True),

            Cuss('"        " SHOULDN\'T HAVE BEEN PREDEFINED', poison=True),
            Cuss('NUMERIC LOCATION FIELD IS ILLEGAL HERE', poison=True),
            Cuss('NO SUCH BANK IN THIS MACHINE', poison=True),

            Cuss('THIS BANK IS FULL', poison=True),
            Cuss('ILLEGAL LOCATION FIELD FORMAT', poison=True),
            Cuss('CARD IGNORED BECAUSE IT\'S TOO LATE IN THE DECK', poison=True),

            Cuss('CARD IGNORED BECAUSE IT MAKES MEMORY TABLE TOO LONG', poison=True),
            Cuss('NO MATCH FOUND FOR CARD NUMBER OR ACCEPTOR TEXT', poison=True),
            Cuss('FIRST CARD NUMBER NOT LESS THAN SECOND', poison=True),

            Cuss('QUEER INFORMATION IN COLUMN 1'),
            Cuss('QUEER INFORMATION IN COLUMN 17'),
            Cuss('QUEER INFORMATION IN COLUMN 24'),

            Cuss('BLANK ADDRESS FIELD EXPECTED'),
            Cuss('ADDRESS FIELD SHOULD CONTAIN A POLISH OPERATOR', poison=True),
            Cuss('OVERFLOW IN POLISH OPERATOR WORD', poison=True),

            Cuss('FIRST ADDRESS OF AN EQUATION MUST BE POSITIVE', poison=True),
            Cuss('FIRST POLISH OPERATOR ILLEGAL INDEXED', poison=True),
            Cuss('SECOND POLISH OPERATOR ILLEGAL INDEXED', poison=True),

            Cuss('NO MATCH FOUND FOR SECOND CARD NUMBER', poison=True),
            Cuss('LAST OPERATOR WORD COUNT WRONG', poison=True),
            Cuss('THIS CODE MAY BECOME OBSOLETE'),

            Cuss(''),
            Cuss(''),
            Cuss(''),

            Cuss(''),
            Cuss(''),
            Cuss(''),

            Cuss('ASTERISK ILLEGAL ON THIS OP CODE', poison=True),
            Cuss(''),
            Cuss(''),

            Cuss('SUBROUTINE NAME NOT RECOGNIZED', poison=True),
            Cuss('MULTIPLE CALLS IN ONE PROGRAM OR SUBRO'),
            Cuss('CONFLICT WITH EARLIER HEAD SPECIFICATION', poison=True),
        ]

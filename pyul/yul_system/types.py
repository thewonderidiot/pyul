# Months
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

# Non-Blank Terminating Characters
NBTCS = '-:+*/,'

# H-1800 alphabet sorting
ALPHABET = '0123456789\'=: ¢&+ABCDEFGHI;.)%■Δ-JKLMNOPQR#$*"↓?◇/STUVWXYZ@,(␍⌑⊗'

# H-1800 max word
ONES = 0xFFFFFFFFFFFF

# Bad word - original "BAD WORD" in H-1800 character set
BAD_WORD = 0xBADBADBADBAD

class Bit:
    BIT1  = (1 << 47)
    BIT2  = (1 << 46)
    BIT3  = (1 << 45)
    BIT4  = (1 << 44)
    BIT5  = (1 << 43)
    BIT6  = (1 << 42)
    BIT7  = (1 << 41)
    BIT8  = (1 << 40)
    BIT9  = (1 << 39)
    BIT10 = (1 << 38)
    BIT11 = (1 << 37)
    BIT12 = (1 << 36)
    BIT13 = (1 << 35)
    BIT14 = (1 << 34)
    BIT15 = (1 << 33)
    BIT16 = (1 << 32)
    BIT17 = (1 << 31)
    BIT18 = (1 << 30)
    BIT19 = (1 << 29)
    BIT20 = (1 << 28)
    BIT21 = (1 << 27)
    BIT22 = (1 << 26)
    BIT23 = (1 << 25)
    BIT24 = (1 << 24)
    BIT25 = (1 << 23)
    BIT26 = (1 << 22)
    BIT27 = (1 << 21)
    BIT28 = (1 << 20)
    BIT29 = (1 << 19)
    BIT30 = (1 << 18)
    BIT31 = (1 << 17)
    BIT32 = (1 << 16)
    BIT33 = (1 << 15)
    BIT34 = (1 << 14)
    BIT35 = (1 << 13)
    BIT36 = (1 << 12)
    BIT37 = (1 << 11)
    BIT38 = (1 << 10)
    BIT39 = (1 << 9)
    BIT40 = (1 << 8)
    BIT41 = (1 << 7)
    BIT42 = (1 << 6)
    BIT43 = (1 << 5)
    BIT44 = (1 << 4)
    BIT45 = (1 << 3)
    BIT46 = (1 << 2)
    BIT47 = (1 << 1)
    BIT48 = (1 << 0)

class SwitchBit:
    RENUMBER          = Bit.BIT1
    CUSSES_ON_PAGE    = Bit.BIT1
    MERGE_MODE        = Bit.BIT2
    LEFTOVER          = Bit.BIT2
    TAPE_KEPT         = Bit.BIT3
    OWE_HEADS         = Bit.BIT3
    ANOTHER_TASK      = Bit.BIT4
    KNOW_SUBS         = Bit.BIT5
    SEGMENT           = Bit.BIT7
    PREVIOUS_INDEX    = Bit.BIT7
    BEFORE            = Bit.BIT8
    LAST_REM          = Bit.BIT8
    SUBROUTINE        = Bit.BIT9
    REVISION          = Bit.BIT10
    REPRINT           = Bit.BIT11
    VERSION           = Bit.BIT12
    SUPPRESS_INACTIVE = Bit.BIT14
    SUPPRESS_SYMBOL   = Bit.BIT15
    SUPPRESS_OCTAL    = Bit.BIT16
    FREEZE            = Bit.BIT17
    BEGINNING_OF_EQU2 = Bit.BIT17
    CONDISH_INACTIVE  = Bit.BIT18
    CONDISH_SYMBOL    = Bit.BIT19
    CONDISH_OCTAL     = Bit.BIT20
    CURRENT_INDEX     = Bit.BIT28
    BEGINNING_OF_EQU1 = Bit.BIT29
    BAD_ASSEMBLY      = Bit.BIT34
    PRINT             = Bit.BIT44

class HealthBit:
    CARD_TYPE_MASK   = Bit.BIT1 | Bit.BIT2 | Bit.BIT3 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6
    CARD_TYPE_END_OF =        0 |        0 |        0 |        0 |        0 |        0 # 00
    CARD_TYPE_MODIFY =        0 |        0 |        0 |        0 |        0 | Bit.BIT6 # 01
    CARD_TYPE_ENDERR =        0 |        0 |        0 |        0 | Bit.BIT5 |        0 # 02
    CARD_TYPE_CARDNO =        0 |        0 |        0 |        0 | Bit.BIT5 | Bit.BIT6 # 03
    CARD_TYPE_ACCEPT =        0 |        0 |        0 | Bit.BIT4 |        0 |        0 # 04
    CARD_TYPE_DELETE =        0 |        0 |        0 | Bit.BIT4 |        0 | Bit.BIT6 # 05
    CARD_TYPE_REMARK =        0 |        0 |        0 | Bit.BIT4 | Bit.BIT5 |        0 # 06
    CARD_TYPE_RIGHTP =        0 |        0 |        0 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6 # 07
    CARD_TYPE_ALIREM =        0 |        0 | Bit.BIT3 |        0 |        0 |        0 # 10
    CARD_TYPE_MEMORY =        0 |        0 | Bit.BIT3 |        0 |        0 | Bit.BIT6 # 11
    CARD_TYPE_INSTR  =        0 |        0 | Bit.BIT3 |        0 | Bit.BIT5 |        0 # 12
    CARD_TYPE_ILLOP  =        0 |        0 | Bit.BIT3 |        0 | Bit.BIT5 | Bit.BIT6 # 13
    CARD_TYPE_DECML  =        0 |        0 | Bit.BIT3 | Bit.BIT4 |        0 |        0 # 14
    CARD_TYPE_OCTAL  =        0 |        0 | Bit.BIT3 | Bit.BIT4 |        0 | Bit.BIT6 # 15
    CARD_TYPE_EQUALS =        0 |        0 | Bit.BIT3 | Bit.BIT4 | Bit.BIT5 |        0 # 16
    CARD_TYPE_SETLOC =        0 |        0 | Bit.BIT3 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6 # 17
    CARD_TYPE_ERASE  =        0 | Bit.BIT2 |        0 |        0 |        0 |        0 # 20
    CARD_TYPE_2OCTAL =        0 | Bit.BIT2 |        0 |        0 |        0 | Bit.BIT6 # 21
    CARD_TYPE_2DECML =        0 | Bit.BIT2 |        0 |        0 | Bit.BIT5 |        0 # 22
    CARD_TYPE_BLOCK  =        0 | Bit.BIT2 |        0 |        0 | Bit.BIT5 | Bit.BIT6 # 23
    CARD_TYPE_HEAD   =        0 | Bit.BIT2 |        0 | Bit.BIT4 |        0 |        0 # 24
    CARD_TYPE_2LATE  =        0 | Bit.BIT2 |        0 | Bit.BIT4 |        0 | Bit.BIT6 # 25
    CARD_TYPE_SUBRO  =        0 | Bit.BIT2 |        0 | Bit.BIT4 | Bit.BIT5 |        0 # 26
    CARD_TYPE_NWINST =        0 | Bit.BIT2 |        0 | Bit.BIT4 | Bit.BIT5 | Bit.BIT6 # 27
    CARD_TYPE_EVEN   =        0 | Bit.BIT2 | Bit.BIT3 |        0 |        0 |        0 # 30
    CARD_TYPE_COUNT  =        0 | Bit.BIT2 | Bit.BIT3 |        0 |        0 | Bit.BIT6 # 31
    CARD_TYPE_SEGNUM =        0 | Bit.BIT2 | Bit.BIT3 |        0 | Bit.BIT5 |        0 # 32

    SYMBOLIC       = Bit.BIT8
    ASTERISK       = Bit.BIT11
    UNDEFINED      = Bit.BIT11
    NEARLY_DEFINED = Bit.BIT12
    MEANINGLESS    = Bit.BIT13
    ILL_DEFINED    = Bit.BIT14
    OVERSIZE       = Bit.BIT14
    POLISH         = Bit.BIT32

class FieldCodBit:
    SYMBOLIC  = Bit.BIT1
    NUMERIC   = Bit.BIT2
    DECIMAL   = Bit.BIT3
    POSITIVE  = Bit.BIT5
    UNSIGNED  = Bit.BIT6

class LocStateBit:
    SYMBOLIC   = Bit.BIT8
    OVERSIZE   = Bit.BIT14
    WRONG_TYPE = Bit.BIT15
    CONFLICT   = Bit.BIT16
    FULL       = Bit.BIT17

class MemType:
    ERASABLE = Bit.BIT25
    FIXED    = Bit.BIT26
    SPEC_NON = Bit.BIT27
    MEM_MASK = ERASABLE | FIXED | SPEC_NON

class Line:
    def __init__(self, text=' '*120, spacing=0):
        self.spacing = spacing
        self.text = text

class Symbol:
    def __init__(self, name, value=0, health=0, definer=None):
        self.name = name
        self.health = health
        self.value = value
        self.definer = definer
        self.definees = []
        self.defined = False
        self.analyzer = 0
        self.def_page = 0
        self.ref_pages = []
        self.index = 0

class SymbolTable:
    def __init__(self):
        self._symbols = []
        self._sym_map = {}
        self._get_latest = True

    def get_latest(self):
        self._get_latest = True

    def get_first(self):
        self._get_latest = False

    def advance(self, name):
        self._sym_map[name] = self._sym_map[name][1:] + self._sym_map[name][0:1]

    def add(self, symbol):
        sym_idx = len(self._sym_map)
        if sym_idx >= 8192:
            return False

        symbol.index = sym_idx
        self._symbols.append(symbol)

        if symbol.name in self._sym_map:
            self._sym_map[symbol.name].append(sym_idx)
        else:
            self._sym_map[symbol.name] = [sym_idx]

        return True

    def first(self, sym_name):
        return self._symbols[self._sym_map[name][0]]

    def all(self, sym_name):
        indices = self._sym_map[sym_name]
        return [self._symbols[i] for i in indices]

    def names(self):
        return list(self._sym_map.keys())

    def symbols(self):
        return self._symbols

    def count(self):
        return len(self._sym_map) + sum([1 if len(defs) > 1 else 0 for defs in self._sym_map])

    def __contains__(self, sym):
        return sym in self._sym_map

    def __getitem__(self, name):
        if isinstance(name, str):
            if name not in self._sym_map:
                if len(self._sym_map) >= 8192:
                    return None
                else:
                    return Symbol(name)

            latest_def = self._sym_map[name][-1 if self._get_latest else 0]
            return self._symbols[latest_def]
        else:
            return self._symbols[name]

from yul_system.assembler.pass1 import Pass1
from yul_system.types import MemType, SwitchBit, Bit, HealthBit, FieldCodBit

class Agc4Pass1(Pass1):
    def __init__(self, mon, yul):
        super().__init__(mon, yul)

        self.max_num_op = 7
        self.max_loc = 0o71777
        self.adr_limit = 0o72000
        self.blok_ones = 0o1777
        self.mod_shift = 24
        self.blok_shif = 10
        self.bank_inc = 0
        self.subr_loc = 1024
        self.m_typ_tab = [
            (MemType.SPEC_NON,    0o57),
            (MemType.ERASABLE,  0o1777),
            (MemType.FIXED,    0o31777),
            (MemType.SPEC_NON, 0o41777),
            (MemType.FIXED,    0o71777),
        ]
        self.op_thrs = {
            # CODES 01
            'MASK':   0o7400,
            'DEC':    self.decimal,
            'DAD':    0o4341,
            'DDV':    0o4641,
            'HEAD':   self.head_tail,
            'MEMORY': self.late_mem,
            # CODES 11
            'DV':     0o6600,
            'MSK':    0o7400,
            'DSU':    0o4441,
            'DSQ':    0o5331,
            'MXV':    0o5241,
            # CODES 10
            'MP':     0o6200,
            'DMP':    0o4541,
            'DMPR':   0o5101,
            'DOT':    0o5641,
            'UNIT':   0o4231,
            'DMOVE':  0o5531,
            'DOUBLE': 0o7002,
            # CODES 21
            'AD':     0o7000,
            'NDX':    0o5040,
            'VAD':    0o5341,
            'ACOS':   0o4731,
            'ABS':    0o4531,
            'ABVAL':  0o4331,
            'VDEF':   0o5731,
            'ADRES':  0o4060,
            'RETURN': 0o4006,
            'NEXT':   0o5711,
            'RELINT': 0o5016,
            'RESUME': 0o5026,
            # CODES 20
            '':       0o4100,
            # CODES 31
            'IS':     self.is_equals,
            'EXTEND': 0o5132,
            'EVEN':   self.even,
            'ITC':    0o4041,
            'ITCQ':   0o5751,
            'VXM':    0o5301,
            'VSU':    0o4141,
            'VSRT':   0o5501,
            'VSLT':   0o5541,
            'VXSC':   0o4101,
            'VXV':    0o5701,
            'EXIT':   0o4011,
            'RTB':    0o4051,
            'AXT,1':  0o4111,
            'AXT,2':  0o4151,
            'AXC,1':  0o5211,
            'AXC,2':  0o5251,
            'VSQ':    0o4431,
            'AST,1':  0o5111,
            'AST,2':  0o5151,
            'ASIN':   0o4631,
            'ITA':    0o5511,
            'ITCI':   0o5551,
            # CODES 30
            'INDEX':  0o5040,
            'EQUALS': self.is_equals,
            'ERASE':  self.erase,
            'NOLOD':  0o5411,
            'NOLOAD': 0o5411,
            'ROUND':  0o5451,
            'VMOVE':  0o4131,
            'INCR,1': 0o4611,
            'INCR,2': 0o4651,
            'VPROJ':  0o5741,
            'NOOP':   0o5402,
            'INHINT': 0o5022,
            # CODES 41
            'OCT':    self.octal,
            'OCTAL':  self.octal,
            '2DEC':   self._2decimal,
            'SETLOC': self.setloc,
            'BANK':   self.agc4_bank,
            'BHIZ':   0o4401,
            'BDSU':   0o4501,
            'BDDV':   0o4701,
            'SIGN':   0o5201,
            'SIN':    0o5031,
            'SGN':    0o5201,
            'SEGNUM': self.late_mem,
            # CODES 51
            'SU':     0o7200,
            'STORE':  0o4110,
            'OVSK':   0o6402,
            'OVIND':  0o6420,
            'SWITCH': 0o5651,
            'BZE':    0o5401,
            'STZ':    0o4241,
            'BVSU':   0o5441,
            'SXA,1':  0o4411,
            'SXA,2':  0o4451,
            'SUBRO':  self.subro,
            # CODES 50
            'BPL':    0o5601,
            'BMN':    0o4201,
            'BOV':    0o4301,
            'SQRT':   0o5231,
            'SMOVE':  0o5631,
            '2OCT':   self._2octal,
            '2OCTAL': self._2octal,
            'BLOCK':  self.agc4_blok,
            'SQUARE': 0o6202,
            # CODES 61
            'TC':     0o4000,
            'XCH':    0o5400,
            'CCS':    0o4430,
            'CAF':    0o5410,
            'TEST':   0o5611,
            'XCHX,1': 0o4511,
            'XCHX,2': 0o4551,
            'XAD,1':  0o4711,
            'XAD,2':  0o4751,
            'TIX,1':  0o5311,
            'TIX,2':  0o5351,
            'TAD':    0o4741,
            'TCR':    0o4000,
            'TCAA':   0o6412,
            'XAQ':    0o4002,
            'CADR':   0o4070,
            'XCADR':  0o4120,
            'TAIL':   self.head_tail,
            # CODES 60
            '=':      self.is_equals,
            'P':      0o4100,
            # CODES 71
            'CS':     0o6000,
            'TS':     0o6450,
            'TSU':    0o5141,
            'TSRT':   0o5041,
            'TSLT':   0o4601,
            'TSLC':   0o5001,
            'LXA,1':  0o4211,
            'LXA,2':  0o4251,
            'LXC,1':  0o4311,
            'LXC,2':  0o4351,
            'XSU,1':  0o5011,
            'XSU,2':  0o5051,
            # CODES 70
            'COM':    0o6002,
            'LOC':    self.setloc,
            'LODON':  0o5711,
            'TMOVE':  0o4031,
            'TP':     0o4031,
            'COMP':   0o5431,
            'COS':    0o5131,
            'COUNT':  self.count,
            '=PLUS':  self.equ_plus,
            '=MINUS': self.equ_minus,
        }

    def m_special(self):
        self._op_found = self.polish_q
        # FIXME: Change AGC4 memory table if segment assembly
        self.post_spec()

    def polish_q(self, popo, opcode):
        if (opcode & 0o1) == 0:
            # Send bits as usual if not polish.
            popo.health |= opcode << 16

            # Exit if an implied address code.
            if opcode & 0o2:
                return

            # Branch if not a polish or store address.
            if (opcode & 0o370) < 0o70:
                return

            if 0o120 < (opcode & 0o370):
                return

            # Reset indicator, exit.
            self._yul.switch &= ~SwitchBit.BEGINNING_OF_EQU1
            return
        
        # Send equivalent of left operator.
        b18t24m = (Bit.BIT18 * 2 - 1) - (Bit.BIT25 * 2 - 1)
        popo.health |= (opcode << 21) & b18t24m
        # Indicate polish operator word.
        popo.health |= HealthBit.POLISH

        two_polop_7 = (0o7 << 17)

        # Branch if not beginning of equation.
        if not self._yul.switch & SwitchBit.BEGINNING_OF_EQU1:
            # Send indication to pass 2.
            popo.health |= two_polop_7
            # Set indicator and exit.
            self._yul.switch |= SwitchBit.BEGINNING_OF_EQU1
            return

        # Decode address field.
        adr_wd, _ = self.adr_field(popo)
        # Fast exit for blank (vacuous) operator.
        if self._field_cod[0] == 0:
            return

        # Branch if address field is not symbolic.
        if self._field_cod[0] != FieldCodBit.SYMBOLIC:
            # Send indication to pass 2.
            popo.health |= two_polop_7
            # Set indicator and exit.
            self._yul.switch |= SwitchBit.BEGINNING_OF_EQU1
            return

        # Branch if no modifier.
        if self._field_cod[1] != 0:
            # Indicate improper address field, exit.
            popo.health |= two_polop_17
            return

        # FIXME: Handle detached asterisk?

        adr_wd = adr_wd.strip()

        if adr_wd[-1] == '*':
            # Blank out attached asterisk.
            adr_wd = adr_wd[:-1]

        two_polop_27 = (0o27 << 17)
        # Branch if more than six characters or polish operator not found.
        if len(adr_wd) > 6 or adr_wd not in self.op_thrs:
            # Indicate failure and exit.
            popo.health |= two_polop_27
            return

        # Send equivalent of right operator.
        second_opcode = self.op_thrs[adr_wd] & ~Bit.BIT37
        b25t31m = 0o77400000
        popo.health |= (second_opcode << 14) & b25t31m

    def agc4_bank(self, popo):
        return self.block(popo)

    def agc4_blok(self, popo):
        self.blok_shif = 8
        result = self.block(popo)
        self.blok_shif = 10
        return result

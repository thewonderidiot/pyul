from yul_system.assembler.pass1 import Pass1
from yul_system.types import MemType, SwitchBit, Bit, HealthBit, FieldCodBit

class Blk2Pass1(Pass1):
    def __init__(self, mon, yul):
        super().__init__(mon, yul)

        self.max_num_op = 7
        self.max_loc = 0o167777
        self.adr_limit = 0o170000
        self.blok_ones = 0o1777
        self.mod_shift = 24
        self.blok_shif = 10
        self.bank_inc = 0
        self.subr_loc = 2048
        self.m_typ_tab = [
            (MemType.SPEC_NON,     0o57),
            (MemType.ERASABLE,   0o3777),
            (MemType.FIXED,     0o13777),
            (MemType.SPEC_NON,  0o17777), # Banks 02 and 03 access fixed-fixed.
            (MemType.FIXED,    0o117777),
            (MemType.SPEC_NON, 0o167777),
        ]
        self.op_thrs = {
            # CODES 01
            'MASK':   0o7400,
            'DCA':    0o5420,
            'DCS':    0o6020,
            'DAS':    0o5010,
            'DIM':    0o5330,
            'DAD':    0o4331,
            'DDV':    0o4211,
            'DCOMP':  0o5221,
            'DCOM':   0o6206,
            'DDOUBL': 0o5042,
            'DEC':    self.decimal,
            '4DNADR': self.blk2_4dnadr,
            'HEAD':   self.head_tail,
            'MEMORY': self.late_mem,
            # CODES 11
            'DXCH':   0o6510,
            'QXCH':   0o5130,
            'MSU':    0o5030,
            'DV':     0o4430,
            'MSK':    0o7400,
            'DSU':    0o4311,
            'DSQ':    0o5201,
            'MXV':    0o4131,
            'DTCB':   0o6456,
            'DTCF':   0o6452,
            # CODES 10
            'MP':     0o7420,
            'DMP':    0o4351,
            'DMPR':   0o4201,
            'DOT':    0o4261,
            'UNIT':   0o5241,
            'DLOAD':  0o4061,
            'DOUBLE': 0o7002,
            'MM':     0o5740,
            'DNCHAN': self.blk2_dnchan,
            'DNPTR':  self.blk2_dnptr,
            # CODES 21
            'AD':     0o7000,
            'ADS':    0o5310,
            'ADRES':  0o4340,
            'ECADR':  0o4360,
            'EBANK=': self.blk2_ebank,
            'REMADR': 0o4344,
            'VAD':    0o4231,
            'ACOS':   0o5171,
            'ABS':    0o5251,
            'ABVAL':  0o5331,
            'VDEF':   0o5231,
            'VCOMP':  0o5321,
            'READ':   0o4034,
            'RAND':   0o4134,
            'RELINT': 0o4016,
            '1DNADR': 0o4360,
            '5DNADR': self.blk2_5dnadr,
            'RESUME': 0o6442,
            'RETURN': 0o4012,
            'EDRUPT': 0o4272,
            'NDX':    0o6450,
            # CODES 20
            '':       0o4754,
            # CODES 31
            'EXTEND': 0o4132,
            'AUG':    0o5230,
            'AXT,1':  0o4451,
            'AXT,2':  0o4451,
            'AXC,1':  0o4461,
            'AXC,2':  0o4461,
            'VXM':    0o4161,
            'VSU':    0o4241,
            'VSL':    0o4431,
            'VSR':    0o4441,
            'VXSC':   0o4031,
            'V/SC':   0o4071,
            'VXV':    0o4271,
            'RTB':    0o4651,
            'VSQ':    0o5261,
            'ASIN':   0o5161,
            'EXIT':   0o5121,
            'VSL1':   0o5601,
            'VSR1':   0o5611,
            'VSL2':   0o5621,
            'VSR2':   0o5631,
            'VSL3':   0o5641,
            'VSR3':   0o5651,
            'VSL4':   0o5661,
            'VSR4':   0o5671,
            'VSL5':   0o5701,
            'VSR5':   0o5711,
            'VSL6':   0o5721,
            'VSR6':   0o5731,
            'VSL7':   0o5741,
            'VSR7':   0o5751,
            'VSL8':   0o5761,
            'VSR8':   0o5771,
            'ITA':    0o4641,
            'ITCQ':   0o5301,
            'RXOR':   0o4334,
            'NV':     0o5744,
            'EVEN':   self.even,
            'IS':     self.is_equals,
            'RVQ':    0o5301,
            # CODES 30
            'INDEX':  0o6450,
            'EQUALS': self.is_equals,
            'ERASE':  self.erase,
            'INHINT': 0o4022,
            'INCR':   0o5210,
            'VLOAD':  0o4001,
            'VPROJ':  0o4301,
            'INCR,1': 0o4531,
            'INCR,2': 0o4531,
            'NORM':   0o4171,
            'INV':    0o5011,
            'INVERT': 0o5011,
            'INVGO':  0o4771,
            'ROUND':  0o5211,
            'ARCSIN': 0o5161,
            'ARCCOS': 0o5171,
            'ZL':     0o5052,
            'ZQ':     0o5252,
            'ROR':    0o4234,
            'VN':     0o5744,
            'NOOP':   0o4402,
            # CODES 41
            'OCT':    self.octal,
            '2DEC':   self._2decimal,
            'SETLOC': self.setloc,
            'BANK':   self.blk2_bank,
            '2BCADR': self.blk2_2bcadr,
            '2CADR':  self.blk2_2bcadr,
            '2FCADR': self.blk2_2fcadr,
            'BBCON':  0o4364,
            'FCADR':  0o4350,
            'BDSU':   0o4321,
            'BDDV':   0o4221,
            'SIGN':   0o4021,
            'SETPD':  0o4361,
            'SET':    0o4751,
            'SETGO':  0o4731,
            'BHIZ':   0o4661,
            'SIN':    0o5141,
            'SINE':   0o5141,
            'WAND':   0o4174,
            'OCTAL':  self.octal,
            'SBANK=': self.blk2_sbank,
            '2DNADR': self.blk2_2dnadr,
            '6DNADR': self.blk2_6dnadr,
            'SEGNUM': self.late_mem,
            # CODES 51
            'SU':     0o7030,
            'BZF':    0o4424,
            'BZMF':   0o7024,
            'BVSU':   0o4251,
            'SSP':    0o4111,
            'BZE':    0o4571,
            'STORE':  0o4760,
            'STODL':  0o4764,
            'STOVL':  0o4770,
            'STCALL': 0o4774,
            'SXA,1':  0o4511,
            'SXA,2':  0o4511,
            'STADR':  0o5271,
            'STQ':    0o4641,
            'SUBRO':  self.subro,
            'OVSK':   0o6462,
            # CODES 50
            'WRITE':  0o4074,
            'BPL':    0o4611,
            'BMN':    0o4621,
            'BOV':    0o4711,
            'BOVB':   0o4701,
            'SQRT':   0o5131,
            'SLOAD':  0o4101,
            'SLC':    0o4171,
            'SL':     0o4371,
            'SR':     0o4401,
            'SLR':    0o4411,
            'SRR':    0o4421,
            'BONSET': 0o4721,
            'BOFSET': 0o4741,
            'BONINV': 0o4761,
            'BOFINV': 0o5001,
            'BONCLR': 0o5021,
            'BOFCLR': 0o5041,
            'BON':    0o5061,
            'BOF':    0o5101,
            'BOFF':   0o5101,
            'SL1R':   0o5401,
            'SR1R':   0o5411,
            'SL1':    0o5421,
            'SR1':    0o5431,
            'SL2R':   0o5441,
            'SR2R':   0o5461,
            'SL2':    0o5461,
            'SR2':    0o5471,
            'SL3R':   0o5501,
            'SR3R':   0o5511,
            'SL3':    0o5521,
            'SR3':    0o5531,
            'SL4R':   0o5541,
            'SR4R':   0o5551,
            'SL4':    0o5561,
            'SR4':    0o5571,
            'WOR':    0o4274,
            'BLOCK':  self.blk2_blok,
            'BNKSUM': self.blk2_bnksm,
            'SQUARE': 0o7602,
            '2OCT':   self._2octal,
            '2OCTAL': self._2octal,
            # CODES 61
            'TCF':    0o4404,
            'CA':     0o5400,
            'XCH':    0o6710,
            'CCS':    0o4410,
            'CAF':    0o5404,
            'TC':     0o4000,
            'CAE':    0o5410,
            'PDDL':   0o4121,
            'PDVL':   0o4141,
            'CALL':   0o4631,
            'CALRB':  0o5071,
            'XCHX,1': 0o4521,
            'XCHX,2': 0o4521,
            'XAD,1':  0o4551,
            'XAD,2':  0o4551,
            'TIX,1':  0o4541,
            'TIX,2':  0o4541,
            'TAD':    0o4011,
            'CGOTO':  0o4041,
            'CCALL':  0o4151,
            'CCLRB':  0o5111,
            'TCR':    0o4000,
            'TCAA':   0o6466,
            'CADR':   0o4350,
            'GENADR': 0o4354,
            '3DNADR': self.blk2_3dnadr,
            'TAIL':   self.head_tail,
            # CODES 60
            '=':      self.is_equals,
            'P':      0o4754,
            # CODES 71
            'CS':     0o6000,
            'TS':     0o6610,
            'LXCH':   0o5110,
            'LXA,1':  0o4471,
            'LXA,2':  0o4471,
            'LXC,1':  0o4501,
            'LXC,2':  0o4501,
            'PUSH':   0o5311,
            'XSU,1':  0o4561,
            'XSU,2':  0o4561,
            'XXALQ':  0o4002,
            # CODES 70
            'COM':    0o6002,
            'GOTO':   0o4601,
            'GO TO':  0o4601,
            'CLR':    0o5051,
            'CLEAR':  0o5051,
            'COS':    0o5151,
            'COSINE': 0o5151,
            'TLOAD':  0o4051,
            'CLRGO':  0o5031,
            'XLQ':    0o4006,
            'COUNT':  self.count,
            'LOC':    self.setloc,
            '=PLUS':  self.equ_plus,
            '=MINUS': self.equ_minus,
        }

    def m_special(self):
        self._op_found = self.polish_q
        # FIXME: Change BLK2 memory table if segment assembly
        self.post_spec()

    # Spucial BANK, BLOCK, 2FCADR, and 2(B)CADR code introductions.
    def blk2_bank(self, popo):
        # Set up to increase bank number by 4.
        self.bank_inc = 4
        return self.block(popo)

    def blk2_blok(self, popo):
        # Set up to do block procedure normally.
        self.bank_inc = 0
        return self.block(popo)

    def blk2_2fcadr(self, popo):
        # 2FCADR is a dobule precision adr. const.
        popo.health |= (0o370 << 16)
        popo.health |= HealthBit.CARD_TYPE_INSTR
        return self._2oct_2dec(popo)

    def blk2_2bcadr(self, popo):
        # 2BCADR is a dobule precision adr. const.
        popo.health |= (0o374 << 16)
        popo.health |= HealthBit.CARD_TYPE_INSTR
        return self._2oct_2dec(popo)

    # Pass 1 processing of the EBANK=, SBANK=, and BNKSUM codes.
    def blk2_ebank(self, popo):
        # EBANK= establishes an E-bank for pass 2 chekcing of references.
        popo.health |= (0o740 << 16)
        popo.health |= HealthBit.CARD_TYPE_NWINST
        return self.nd_setloc(popo)

    def blk2_sbank(self, popo):
        # SBANK= establishes an S-bank for pass 2 chekcing of references.
        popo.health |= (0o744 << 16)
        popo.health |= HealthBit.CARD_TYPE_NWINST
        return self.nd_setloc(popo)

    def blk2_bnksm(self, popo):
        # BNKSUM forms TC self pairs at bank ends.
        popo.health |= (0o750 << 16)
        popo.health |= HealthBit.CARD_TYPE_NWINST
        return self.nd_setloc(popo)

    def blk2_dnptr(self, popo):
        popo.health |= (0o607 << 21)
        return self.instruct(popo)

    def blk2_dnchan(self, popo):
        return self.blk2_dnx(popo, 7)

    def blk2_6dnadr(self, popo):
        return self.blk2_dnx(popo, 5)

    def blk2_5dnadr(self, popo):
        return self.blk2_dnx(popo, 4)

    def blk2_4dnadr(self, popo):
        return self.blk2_dnx(popo, 3)

    def blk2_3dnadr(self, popo):
        return self.blk2_dnx(popo, 2)

    def blk2_2dnadr(self, popo):
        return self.blk2_dnx(popo, 1)

    def blk2_dnx(self, popo, num):
        popo.health |= (num << 27)
        opcode = self.op_thrs['ECADR'] & ~Bit.BIT37
        return self._op_found(popo, opcode)

    # Special routine in pass 1 for BLK2 to respond to the finding of an instruction operatio ncode. If
    # the code is a basic instruction or an address constant, sets 11 bits into health as usual, and returns to the
    # general instruction-processing procedure. If the code is a polish operator, the seven-bit equivalent is placed
    # in bits 18-24 of health and the address field, with indexing asterisk (if any) blanked out, is interpreted as
    # follows: blank: operator 136 (internal codes), with any other format but pure symbolic: operator 137, symblic: value
    # from table of internal codes if polish operator, or operator 137 otherwise.

    def polish_q(self, popo, opcode):
        if (opcode & 0o1) == 0:
            # Send bits as usual if not polish.
            popo.health |= opcode << 16
            return

        # Send equivalent of left operator.
        b18t24m = (Bit.BIT18 * 2 - 1) - (Bit.BIT25 * 2 - 1)
        popo.health |= (opcode << 21) & b18t24m

        # Plant polish bit and operator 136.
        blank_op_2 = 0o57200000
        popo.health |= blank_op_2

        # Decode address field.
        adr_wd, _ = self.adr_field(popo)

        # Fast exit for blank (vacuous) operator.
        if self._field_cod[0] == 0:
            return

        # Branch if address field is not symbolic.
        if self._field_cod[0] != FieldCodBit.SYMBOLIC:
            return self.pole_fail(popo)

        # Branch if no modifier.
        if self._field_cod[1] != 0:
            return self.pole_fail(popo)

        # FIXME: Handle detached asterisk?

        adr_wd = adr_wd.strip()

        if adr_wd[-1] == '*':
            # Blank out attached asterisk.
            adr_wd = adr_wd[:-1]

        # Branch if more than six characters or polish operator not found.
        if len(adr_wd) > 6 or adr_wd not in self.op_thrs:
            return self.pole_fail(popo)

        # Branch if find is not a polish operator.
        b37b48m = Bit.BIT37 | Bit.BIT48
        second_opcode = self.op_thrs[adr_wd]

        if (second_opcode & b37b48m) != b37b48m:
            return self.pole_fail(popo)

        # Send internal code for 2nd operator.
        b25t31m = 0o77400000
        popo.health &= ~b25t31m
        popo.health |= (second_opcode << 14) & b25t31m

    def pole_fail(self, popo):
        popo.health |= Bit.BIT31

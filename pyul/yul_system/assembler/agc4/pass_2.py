from yul_system.assembler.pass_2 import Pass2

class AGC4Pass2(Pass2):
    def __init__(self, mon, yul, adr_limit):
        super().__init__(mon, yul, adr_limit)

from yul_system.types import ALPHABET

class Cuss:
    def __init__(self, msg, poison=False):
        self.msg = msg
        self.poison = poison
        self.requested = False

class Pass2:
    def __init__(self, mon, yul, adr_limit):
        self._mon = mon
        self._yul = yul
        self._adr_limit = adr_limit
        self._def_xform = 0o31111615554

    def pass_1p5(self):
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
        definer.health = 0
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
        pass

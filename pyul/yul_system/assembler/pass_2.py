from yul_system.types import ALPHABET, SwitchBit

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
        self._marker = '*'
        self._line = ' '*120
        self._old_line = ' '*120

    def pass_2(self):
        for popo in self._yul.popos:
            # Clear location symbol switch.
            self._equaloc = 0
            # Branch if last card wasnt remarks
            if self._yul.switch & SwitchBit.LAST_REM:
                self._yul.switch &= ~SwitchBit.LAST_REM
                # Branch if this card isnt right print.
                if (popo.health & HealthBit.CARD_TYPE_MASK) == HealthBit.CARD_TYPE_RIGHTP:
                    # Branch if line unaffected by this rev.
                    vert_format = ord(popo.card[7])
                    if vert_format & 0x10:
                        self._old_line = self._old_line[:7] + self._marker + self._marker[8:]
                        self._marker = '*'

                    self.send_sypt(popo.card)

                    # Set right print remarks in print.
                    self._old_line = self._old_line[:80] + popo.card[8:48]

                    # Branch if no right print cardno error.
                    if not popo.health & Bit.BIT7:
                        self.cusser()
                        continue

                    # Make up card number error note.
                    self._line = self._line[:88] + self.cuss_list[0].msg
                    if self.cuss_list[0].requested:
                        self.rem_cn_err(popo)
                        continue
            else:
                self.rem_cn_err(popo)

        return self.end_pass_2()

    def rem_cn_err(self, popo):
        pass

    def end_pass_2(self):
        pass

    def send_sypt(self, card):
        pass

    def cusser(self):
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

        self._err_pages = 0

        return self.pass_2()

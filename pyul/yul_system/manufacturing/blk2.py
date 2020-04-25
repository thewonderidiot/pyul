import struct

class ManufacturingBlk2:
    def __init__(self, mon, yul, bypt):
        self._mon = mon
        self._yul = yul
        self._bypt = bypt
        self._b2_subdrs = {
            'PUNCH':   self.blk2_pnch,
            'COPY':    self.blk2_copy,
            'COMPARE': self.blk2_cmpr,
        }

        self._allow_e = False
        self._by_pas_mdn = False
        self._req_place = 0

    def what_subd(self, card, sentence):
        if sentence[0] in self._b2_subdrs:
            self._b2_subdrs[sentence[0]](card, sentence)
        else:
            self._yul.howz_that(card, sentence[0])

    def blk2_pnch(self, card, sentence):
        if sentence[1] != '36K':
            return self.rayth_pq(card, sentence)

    # *PUNCH RAYTHEON WIRING TAPE* subdirector subroutine here. Each substrand is a separate piece of paper.
    # At least one of the subdirectors *PARAGRAPH* is required.
    # Subdirector *MODULE DECK NUMBERS* is required.
    # Subdirector *USE* is optional.
    # Subdirector *TESTING* is optional.
    def rayth_pq(self, card, sentence):
        # Branch if wd 2 not "CORE" or "RAYTHEON".
        word = 1
        if sentence[word] != 'RAYTHEON':
            return self.try_mastr(card, sentence, word)

        # "WIRING" is required.
        word += 1
        if sentence[word] != 'WIRING':
            return self.rayth_tt(card, sentence, word)

        # Go quiz rest of subdirector.
        word += 1
        self.ry_common(card, sentence, word)

        self._mon.mon_typer('PUNCH RAYTHEON WIRING TAPE')

        # Read other task subdirectors
        self.read_a_req()

    def rayth_tt(self, card, sentence, word):
        pass

    # Subroutines common to punching Raytheon wiring tape and Raytheon core rope tester tape
    def ry_common(self, card, sentence, word):
        # "TAPE" is required.
        if sentence[word] != "TAPE":
            self._yul.howz_that(card, sentence[word])

        # Superfluous words are forbidden.
        word += 1
        if sentence[word] != '':
            self._yul.howz_that(card, sentence[word])

        # Zero req list of 240 wds + sentinel.
        self._req_list = [False]*241

        # Go to read & absorb paragraph requests.
        return

    def try_mastr(self, card, sentence, word):
        if sentence[word] != 'MASTER':
            return self.try_symbl(card, sentence, word)

    def try_symbl(self, card, sentence, word):
        if sentence[word] != 'SIMULATION':
            return self.try_binry(card, sentence, word)

    def try_binry(self, card, sentence, word):
        virtualagc = False
        if sentence[word] != 'BINARY':
            self._yul.howz_that(card, sentence[word])

        word += 1
        if sentence[word] == 'FOR':
            word += 1
            if sentence[word] != 'VIRTUALAGC':
                self._yul.howz_that(card, sentence[word])
            word += 1
            virtualagc = True

        if sentence[word] != '':
            self._yul.howz_that(card, sentence[word])

        self._mon.mon_typer('PUNCH BINARY FILE')
        
        # Zero req list of 240 wds + sentinel.
        self._req_list = [False]*241

        self._by_pas_mdn = True
        self.read_a_req()

        bin_fn = self._yul.prog_name + ('.R%u' % self._yul.revno) + '.bin'

        par_data = [None] * 36 * 4

        while True:
            # Get next paragraph
            par = self.get_req_pn()
            if par is None:
                break

            par_id = par['PARAGRAPH']
            if virtualagc:
                if par_id < 0o30:
                    par_id -= 0o10
                else:
                    par_id -= 0o20
            else:
                if par_id >= 0o20:
                    par_id -= 0o20

            par_data[par_id] = b''
            for w in par['WORDS']:
                word = w & 0o177777
                if not virtualagc:
                    word = ((word & 0o1) << 14) | (word & 0o100000) | ((word & 0o77776) >> 1)
                par_data[par_id] += struct.pack('>H', word)

        last_par = None
        first_par = None
        for par_id in range(len(par_data)):
            if par_data[par_id] is None:
                continue

            if first_par is None:
                first_par = par_id

            if last_par is not None and last_par != (par_id - 1):
                for p in range(last_par + 1, par_id):
                    par_data[p] = b'\x00\x00' * 256

            last_par = par_id

        with open(bin_fn, 'wb') as f:
            f.write(b''.join(par_data[first_par:last_par+1]))

    def get_req_pn(self):
        # Find next active paragraph
        found = False
        for p in range(self._req_place, 240):
            if self._req_list[p]:
                # Get paragraph if it exists.
                for par in self._bypt['PARAGRAPHS']:
                    if par['PARAGRAPH'] == p:
                        self._req_place = p + 1
                        return par

                # Type "PARAGRAPH NNN NOT HERE", try next.
                self._mon.mon_typer('PARAGRAPH %03o NOT HERE' % p)

        return None
        
    def blk2_copy(self, card, sentence):
        pass

    def blk2_cmpr(self, card, sentence):
        pass

    # Subroutine to read and absorb subdirectors
    # S     PARAGRAPH ALL
    # S     PARAGRAPH NNN
    # S     PARAGRAPH NNN THRU (THROUGH) NNN
    # The appearance of *PARAGRAPH ALL* forbids any subsequent paragraph subdirectors.
    # The appearance of any paragraph subdirector forbids any subsequent *PARAGRAPH ALL* subdirector.
    # NNN is from 1 to 3 octal digits and is the name of a BLK2 paragraph. A card specifying paragraph N
    # will leave in req list +N a CAC whose CAC2 points to alf "    RHS" (rope, half, side = quarter-rope
    # name), and whose CAC3 points to alf "WWW-WWW", the range of wire numbers that specify the sense-
    # winding set.
    def read_a_req(self):
        got_all = False
        while True:
            # Fetch SS request if any such are left.
            sub_card, sub_sent = self._yul.rd_subdrc()

            # Come here when subdirectors run out.
            if sub_card is None:
                if got_all:
                    # *PARAGRAPH ALL* SD must be only *PARAGRAPH* SD for this task
                    if self._req_list[240]:
                        self._mon.mon_typer('*PARAGRAPH ALL* CARD INVALIDATED BY PREVIOUS CARD')
                        self._yul.typ_abort()

                    # Start search for program first bin rcds.
                    for p in self._bypt['PARAGRAPHS']:
                        self._req_list[p['PARAGRAPH']] = True # FIXME
                else:
                    # Return if any requests were absorbed.
                    if not self._req_list[240]:
                        # Type "NO GOOD REQUESTS', abort.
                        self._mon.mon_typer("NO GOOD REQUESTS")
                        self._yul.typ_abort()

                return self.any_mdn()

            word = 0
            if sub_sent[word] != 'PARAGRAPH':
                self.try_test(sub_card, sub_sent, word)
                continue

            if got_all:
                self.one_only(sub_card)

            # Jump if not *ALL*
            word += 1
            if sub_sent[word] != 'ALL':
                self.list_para(sub_card, sub_sent, word)
                continue

            # No more words allowed.
            word += 1
            if sub_sent[word] != '':
                self._yul.howz_that(sub_card, sub_sent[word])

            # No futher *PARAGRAPH* SD allowed.
            got_all = True

    def list_para(self, sub_card, sub_sent, word):
        par_no = self.chk_para_n(sub_sent[word])

        # Save low paragraph number
        low_no = par_no

        word += 1
        if sub_sent[word] in ('THRU', 'THROUGH'):
            word += 1
            par_no = self.chk_para_n(sub_sent[word])
            
            # No more words allowed in SD.
            word += 1
            if sub_sent[word] != '':
                self._yul.howz_that(sub_card, sub_sent[word])

            # Jump if 1st para not lower than 2nd
            if par_no <= low_no:
                self._yul.howz_that(sub_card, sub_sent[word - 1])

        elif sub_sent[word] != '':
            # No more words allowed.
            self._yul.howz_that(sub_card, sub_sent[word])

        # Set up paragraph data.
        for p in range(low_no, par_no+1):
            if not self._allow_e and p <= 0o7:
                # Para numbers 000 - 007 are illegal
                self._mon.mon_typer('ILLEGAL PARAGRAPH NO.')
                self._yul.ign_sbdir(sub_card)

            if p >= 0o30  and p <= 0o37:
                # Paras numbers 030 - 037 are illegal
                self._mon.mon_typer('ILLEGAL PARAGRAPH NO.')
                self._yul.ign_sbdir(sub_card)

            if self._req_list[p]:
                # Requested paragraph is duplicate.
                self._mon.mon_typer('DUPLICATE PARAGRAPH NO.')
                self._yul.ign_sbdir(sub_card)

            # FIXME
            self._req_list[p] = True

            # Show that at least one request got in.
            self._req_list[240] = True

    def chk_para_n(self, sub_card, alf_n):
        if len(alf_n) > 3:
            # Paragraph number over three digits.
            self._mon.mon_typer('PARAGRAPH NO. TOO LONG')
            self._yul.ign_sbdir(sub_card)

        try:
            par_no = int(alf_n, 8)
        except:
            self._mon.mon_typer('PARAGRAPH NO. NOT OCTAL')
            self._yul.ign_sbdir(sub_card)

        return par_no
            

    def any_mdn(self):
        if self._by_pas_mdn:
            return

    def try_test(self, sub_card, sub_sent, word):
        if sub_sent[word] != 'TESTING':
            return self.try_use(sub_card, sub_sent, word)

    def try_use(self, sub_card, sub_sent, word):
        if sub_sent[word] != 'USE':
            return self.try_modul(sub_card, sub_sent, word)

    def try_modul(self, sub_card, sub_sent, word):
        if sub_sent[word] != 'MODULE':
            self._yul.howz_that(sub_card, sub_sent[0])

    def one_only(self, sub_card):
        self._mon.mon_typer("EXCESS SUBDIRECTOR ENCOUNTERED")
        self._yul.rejec_dir(sub_card)

from datetime import datetime
from yul_system.yulprogs import Yulprogs
from yul_system.assembler import pass1
from yul_system.types import MONTHS, NBTCS, Bit, SwitchBit, SymbolTable

class TypAbort(Exception):
    # Generic task-aborting error.
    pass

class BadSubdirector(Exception):
    # Error raised when a bad subdirector is encountered.
    pass

class NewVers(Exception):
    # This exception is defined as a means to accomplish a direct jump back into the
    # ASSEMBLY routine, in the case PROG ADJ determines a VERSION assembly is being
    # done. The object messages created in such a case are passed back as the
    # arguments to this exception.
    pass

class Yul:
    def __init__(self, mon):
        self._mon = mon
        self._no_typist = False
        self._no_revise = False
        self._non_wise = 0
        self._invisible_director = False
        self.substrab = [False]*256
        self.yulprogs = None
        self.switch = 0
        self.revno = 0
        self.n_err_lins = 0
        self.err_pages = [None, None]
        self._auth_name = ''
        self.prog_name = ''
        self._new_auth_name = ''
        self._new_prog_name = ''
        self.tape = 'YULPROGS'
        self._task_msg = ''
        self._yul_date = ''
        self._yul_log_a = 'A'
        self.n_lines = 54
        self.n_copies = 0
        self.page_head = 'LOGNO.  YUL SYSTEM FOR                  ' + \
                         '                                        ' + \
                         '                        (MAIN)  PAGE   0'
        self.page_no = 0
        self.sym_place = 0

        self._directs = {
            'ADD':           self.add_comp,
            'REMOVE':        self.rmov_comp,
            'MESSAGE':       self.message,
            'DELETE':        self.elim_prsu,
            'ASSEMBLE':      self.assembly,
            'REPRINT':       self.reprint,
            'MANUFACTURE':   self.manufact,
            'CLOSE':         self.clos_mona,
            'CONTROL':       self.control,
            'DECONTROL':     self.decontr,
            'TRANSFER':      self.xfer_psr,
            'PRINT':         self.print_psr,
            'PUNCH':         self.punch_psr,
            'ASSEMBLY':      self.pass_stat,
            'MANUFACTURING': self.manu_stat,
            'CREATE':        self.create_bu,
            'LIST':          self.unready,
        }

    def pass_0(self):
        self.begin_job()
        self.set_pg_hed()

        while True:
            # Branch if there's no invisible director.
            if self._invisible_director:
                # Erase invisible director flag.
                self._invisible_director = False

                # Turn off typewriter for task duration.
                self._no_typist = True

                card = '' # FIXME
            else:
                card = self._mon.phi_read()

            # End job if we got a monitor card or ran out of cards.
            if not card or card[0] == '*':
                break

            # Count non-director cards
            if card[0] != 'Y':
                self._non_wise += 1
                continue

            # Break up Yul direcor card into fields.
            sentence = self._mon.phi_sentr(card)

            # Type count of non-Yul-directors if NZ.
            if self._non_wise > 0:
                self._mon.mon_typer('CARDS BYPASSED: %u' % self._non_wise)
                self._non_wise = 0

            # Normalize contents of columns 2-8.
            abbrev = card[1:7] + self.tape[0] + card[0]
            while abbrev[0] == ' ':
                abbrev = abbrev[1:8] + abbrev[0]

            card = abbrev + card[8:]

            # Initial letter must match that of tape.
            if abbrev[0] != self.tape[0]:
                self._mon.mon_typer('WRONG TAPE NAME ABBREVIATION IN COLS 2-7')
                self.rejec_dir(card)

            # Set up table look-up on 1st word.
            if sentence[0] in self._directs:
                try:
                    self._directs[sentence[0]](card, sentence)
                except TypAbort:
                    pass
            else:
                # Announce unrecognition of first word.
                self.howz_that(card, sentence[0])

        # FIXME: close threads?
        self._mon.mon_typer('END YUL SYSTEM')

    def begin_job(self):
        # Special routine, done at the beginning of a Yul job.

        # FIXME: Set up side groups as dummy threads?

        # Re-sentence-read monitor call card.
        sentence = self._mon.phi_sentr(self._mon.lcard)
        if sentence[1] == '':
            # If there's no word after "YUL", use tape YULPROGS.
            self.tape = 'YULPROGS'
        else:
            # Otherwise, use tape named.
            self.tape = sentence[1]

        self.yulprogs = Yulprogs(self.tape)

        # Append "A" or "B" to log number.
        self._yul_log_a = str(self._mon.get_log_no()) + self._mon.h1800_ab_sw

        # Type "BEGIN YUL SYSTEM".
        self._mon.mon_typer('BEGIN YUL SYSTEM', end='\n\n\n')

        # Format the date
        now = datetime.now()
        self._yul_date = '%s %u, %u' % (MONTHS[now.month-1], now.day, now.year)


    def set_pg_hed(self):
        # Forbid revisions on a frozen tape.
        if self.tape == 'FROZEYUL' or self.tape == '2NDFROZE':
            self._no_revise = True

        # Put log and date in page heading.
        self.page_head = self._yul_log_a + self.page_head[7:90] + self._yul_date + self.page_head[90+len(self._yul_date):]

    def rejec_dir(self, card):
        # Director or subdirector rejected.
        self._mon.mon_typer('THEREFORE THIS CARD IS REJECTED:')
        self.yul_typer(card[8:])
        self.typ_abort()

    def typ_abort(self):
        # Final action, all aborts.
        self._mon.mon_typer('8   TASK ABORT', end='\n\n\n')

        # FIXME: abort things
        raise TypAbort

    def accept_m2(self):
        ## FIXME: call for backup?
        # Type acceptance of name.
        self.yul_typer('ACCEPTED')
        self.yul_typer('', end='\n\n\n')

    def yul_typer(self, s, end='\n'):
        # A silenced typer can be let go by printing 8 blanks
        if self._no_typist and s[0:7] != '        ':
            return
        self._no_typist = False
        #stripped = ' '.join(s.split()) ## FIXME: Need to strip out duplicate blanks?
        self._mon.mon_typer(s, end=end)

    def howz_that(self, card, word):
        # Procedure to cuss an unrecognized word
        self.yul_typer('THIS WORD UNRECOGNIZED: ' + word)
        self.rejec_dir(card)

    def rd_subdrc(self):
        # Subroutine in pass 0 to peek at end sentence-read cards. Returns card contents and
        # parsed sentence if the next card is a subdirector, or None if not.

        # Peek at next card.
        next_card = self._mon.phi_peek()
        if next_card[0] == 'S':
            # Set up for sentence reading.
            self._mon.phi_read()
            # Break down subdirector.
            sentence = self._mon.phi_sentr(next_card)
        else:
            # Not a subdirector.
            next_card = None
            sentence = None

        return next_card, sentence

    def decod_cpn(self, card, sentence, word):
        # Subroutine to decode and standardize a computer name. The word "MOD" is ignored if it
        # precedes the computer name. The raw name is returned. Error exit if name is more than
        # 4 characters long. If the name begins with a digit, it is shifted right 4 characters
        # and "MOD " is inserted (in the sentence only, not in comp name).
        if sentence[word] == 'MOD':
            # Move up sentence to cover "MOD"
            sentence.pop(word)

        if sentence[word] == '':
            # Cuss blank computer name and abort.
            self.yul_typer('COMPUTER NAME IS BLANK.')
            self.rejec_dir(card)

        if len(sentence[word]) > 4:
            # Error if name longer than 4 characters.
            self.yul_typer('TOO-LONG COMPUTER NAME: %s' % sentence[word])
            self.rejec_dir(card)

        self.comp_name = sentence[word]

        self.cpn_fixer(sentence, word)

        return self.comp_name

    def cpn_fixer(self, sentence, word):
        # Exit if name does not begin with digit.
        if sentence[word][0].isnumeric():
            # Insert "MOD"
            sentence[word] = 'MOD ' + sentence[word]

    def add_comp(self, card, sentence):
        word = 1

        # "NEW" is optional here.
        if sentence[word] == 'NEW':
            word += 1

        # "COMPUTER" is required.
        if sentence[word] != 'COMPUTER':
            self.howz_that(card, sentence[word])

        # "NAME" is optional.
        word += 1
        if sentence[word] == 'NAME':
            word += 1

        # Decode computer name.
        computer = self.decod_cpn(card, sentence, word)

        # Superfluous words are forbidden.
        if sentence[word + 1] != '':
            self.howz_that(card, sentence[word + 1])

        # Announce new name.
        self.yul_typer('  NEW COMPUTER: %s' % sentence[word])

        # Cuss and abort if conflict.
        old_comp = self.yulprogs.find_comp(computer)
        if old_comp is not None:
            self._mon.mon_typer('CONFLICT WITH EXISTING COMPUTER NAME')
            self.typ_abort()

        # Form computer name entry.
        self.yulprogs.add_comp(computer)
        self.accept_m2()

    def rmov_comp(self, card, sentence):
        word = 1

        # "OLD" is optional.
        if sentence[word] == 'OLD':
            word += 1

        # "COMPUTER" is required.
        if sentence[word] != 'COMPUTER':
            self.howz_that(card, sentence[word])

        # "NAME" is optional.
        word = word + 1
        if sentence[word] == 'NAME':
            word += 1

        # Decode computer name and announce task.
        comp_name = self.decod_cpn(card, sentence, word)

        self._mon.mon_typer('REMOVING COMPUTER NAME: %s' % sentence[word])

        # Look up computer name.
        old_comp = self.yulprogs.find_comp(comp_name)
        if old_comp is None:
            # Cuss and abort if no such computer.
            self._mon.mon_typer('COMPUTER NAME NOT RECOGNIZED.')
            self.typ_abort()

        # Branch if computer has no programs.
        progs = self.yulprogs.list_progs(comp_name)
        if len(progs) > 0:
            # Cuss about removing computer in use. Tell him to check
            # the directory listing.
            self._mon.mon_typer('COMPUTER IS STILL IN USE')
            self._mon.mon_typer('CHECK DIRECTORY LISTING')
            self.typ_abort()

        # Checking on software sharing.
        other_comp_names = self.yulprogs.list_comps()
        shared_passes = 0
        for other_name in other_comp_names:
            if other_name == comp_name:
                continue

            other_comp = self.yulprogs.find_comp(other_name)
            for p in ('PASS 1', 'PASS 2', 'PASS 3', 'MANUFACTURING'):
                if other_comp[p]['SHARES'] == comp_name:
                    # Type out who needs which software.
                    self._mon.mon_typer('%s STILL NEEDED BY %s' % (p, other_name))
                    shared_passes += 1

        if shared_passes > 0:
            # Abort if there was any sharing.
            self.typ_abort()

        # Remove the computer.
        self.yulprogs.remove_comp(comp_name)
        self.accept_m2()

    def message(self, card, sentence):
        # Routine to startle the operator and give him a message.
        # Make stomping noise before and after.
        self._mon.mon_typer('■■■■■■■■')
        self.yul_typer(card[8:])
        self._mon.mon_typer('■■■■■■■■', end='\n\n\n')

    def elim_prsu(self, card, sentence):
        pass

    def assembly(self, card, sentence):
        self._task_msg = 'ASSEMBLY'
        word = 1
        try:
            # Break down and reform rest of director.
            objc_msg = self.task_objc(card, sentence, word)
            # Type task.
            self.yul_typer(self._task_msg)
            head_msg = objc_msg
        except NewVers as e:
            # Read object messages from created by NEWVERS.
            objc_msg = e.args[0]
            head_msg = e.args[1]

        self.typ_asobj(card, sentence, objc_msg, head_msg)

    def typ_asobj(self, card, sentence, objc_msg, head_msg=None):
        # Type object of task.
        self.yul_typer(objc_msg)

        # Include computer name in page heading.
        if head_msg is None:
            head_msg = objc_msg

        # Omit computer name from "END OF" line.
        self.old_line = '%-60s%12s' % (head_msg, self._yul_date)

        head_comp_msg = '%s: %s' % (self.comp_name, head_msg)
        head_comp_msg = '%-66s' % head_comp_msg

        self.page_head = self.page_head[:23] + head_comp_msg + self.page_head[89:]

        # Seek computer name in directory.
        comp = self.yulprogs.find_comp(self.comp_name)
        if comp is None:
            # Cuss and exit if not there.
            self.yul_typer('COMPUTER NAME NOT RECOGNIZED.')
            self.typ_abort()

        # Branch if passes 1-3 available for it.
        for p in ('PASS 1', 'PASS 2', 'PASS 3'):
            if not comp[p]['AVAILABLE']:
                self.yul_typer('CAN\'T ASSEMBLE FOR THAT COMPUTER')
                self.typ_abort()

        if self._task_msg.split()[0] != 'ASSEMBLY':
            # Branch if doing reprent, not assembly.
            sub_card, sub_sent = self.rd_subdrc()
            if sub_card is None or sub_sent[0] != 'FOR':
                # Require subdirector "FOR CUSTOMERNAME".
                self._mon.mon_typer('REPRINT REQUIRES "FOR WHOM" SUBDIRECTOR')
                self.typ_abort()

            # Type out entire subdirector card.
            self.yul_typer(' '.join(sub_sent))

            # Request reprint, check prg/sub name etc.
            self.switch |= SwitchBit.REPRINT | SwitchBit.MERGE_MODE
            self.known_psr()

            # FIXME: Test obsolescence bit.

        elif self.switch & SwitchBit.VERSION:
            # Branch if doing version assembly.
            self.switch |= SwitchBit.MERGE_MODE

            # Check prog/sub name, revno, author, etc.
            self.known_psr()

            # Recover new progname, force revision.
            self.prog_name = self._new_prog_name
            self.switch |= SwitchBit.REVISION

            # Recoer author name of version.
            self._auth_name = self._new_auth_name

            # Go join procedure for new prog/subro.
            self.new_prsub()

        elif (self.switch & SwitchBit.REVISION) == 0:
            # Branch if new program or subroutine.
            self.new_prsub()

        else:
            # Here alone the revision number is begin changed.
            if self._no_revise:
                # Forbid revisions on a frozen tape.
                self._mon.mon_typer('CAN\'T REVISE A PROGRAM ON A FROZEN TAPE')
                self.typ_abort()

            # Request merging, check program name etc.
            switch |= SwitchBit.MERGE_MODE
            self.known_psr()

        self.init_assy()

    def init_assy(self):
        # Procedure to initialize a permissible assembly or reprint.
        # Initialize symbol table
        self.sym_thr = SymbolTable()

        # Initialize availability table.
        self.av_table = [0]*2048

        # Initialize POPO list
        self.popos = []

        sub_card, sub_sent = self.rd_subdrc()
        while sub_card is not None:
            try:
                self.assy_subd(sub_card, sub_sent, True)
            except BadSubdirector:
                pass
            sub_card, sub_sent = self.rd_subdrc()

        pass1.inish_p1(self._mon, self)

    def assy_subd(self, sub_card, sub_sent, is_assembly):
        # Subroutine in pass 0 to process assembly and/or printing subdirectors.
        word = 0
        if sub_sent[word] == 'PRINT':
            word += 1
            if len(sub_sent[word]) < 1 or len(sub_sent[word]) > 2:
                self._mon.mon_typer('NUMERIC FIELD WRONG SIZE')
                self.ign_sbdir(sub_card)

            try:
                num = int(sub_sent[word], 10)
            except:
                self._mon.mon_typer('NUMERIC WORD NOT DECIMAL')
                self.ign_sbdir(sub_card)

            if num < 2 or num > 63:
                    self.num_rng_er(sub_card)

            word += 1
            if sub_sent[word] == 'LINES':
                if num < 10:
                    self.num_rng_er(sub_card)

                if self.n_lines != 54:
                    self.duplisub(sub_card)

                self.n_lines = num
                self._mon.mon_typer('PRINT %u LINES PER PAGE' % num)
                return

            elif sub_sent[word] == 'COPIES':
                if self.n_copies != 0:
                    self.duplisub(sub_card)

                self.n_copies = num
            
            else:
                self.unrc_sbdr(sub_card, sub_sent[word])

        elif sub_sent[word] == 'RENUMBER':
            if self.switch & SwitchBit.REPRINT:
                # Refuse to renumber during a reprint.
                self.il_reqest(sub_card)

            # Check duplication and call from print.
            self.dup_sub_ch(SwitchBit.RENUMBER, is_assembly, sub_card)

            self.switch |= SwitchBit.RENUMBER
            self._mon.mon_typer('RENUMBER CARDS')
            return

        elif sub_sent[word] == 'SUPPRESS':
            word += 1
            conditional = False
            temp_mask = SwitchBit.CONDISH_SYMBOL | SwitchBit.CONDISH_OCTAL | SwitchBit.CONDISH_INACTIVE
            if sub_sent[word] == 'CONDITIONALLY':
                conditional = True
                word += 1
            else:
                temp_mask |= SwitchBit.SUPPRESS_SYMBOL | SwitchBit.SUPPRESS_OCTAL | SwitchBit.SUPPRESS_INACTIVE

            if sub_sent[word] == 'SYMBOL':
                self.dup_sub_ch(SwitchBit.CONDISH_SYMBOL, is_assembly, sub_card)
                self.switch |= (SwitchBit.CONDISH_SYMBOL | SwitchBit.SUPPRESS_SYMBOL) & temp_mask
                suppressed = ' SYMBOL TABLE LISTING'
            elif sub_sent[word] == 'OCTAL':
                self.dup_sub_ch(SwitchBit.CONDISH_OCTAL, is_assembly, sub_card)
                self.switch |= (SwitchBit.CONDISH_OCTAL | SwitchBit.SUPPRESS_OCTAL) & temp_mask
                suppressed = ' OCTAL STORAGE MAP'
            elif sub_sent[word] == 'INACTIVE':
                self.dup_sub_ch(SwitchBit.CONDISH_INACTIVE, is_assembly, sub_card)
                self.switch |= (SwitchBit.CONDISH_INACTIVE | SwitchBit.SUPPRESS_INACTIVE) & temp_mask
                suppressed = ' INACTIVE SUBROUTINES'
            else:
                self.unrc_sbdr(sub_card, sub_sent[word])

            if conditional:
                self._mon.mon_typer('SUPPRESS', end='')
            else:
                self._mon.mon_typer('SUPPRESS CONDITIONALLY: ', end='')

            self._mon.mon_typer('%s' % suppressed, end='\n\n\n')
            return

        elif sub_sent[word] == 'FREEZE':
            if self.switch & SwitchBit.REPRINT:
                # Refuse to freeze during a reprint.
                self.il_reqest(sub_card)

            word += 1
            if sub_sent[word] != 'SUBROUTINES':
                self.unrc_sbdr(sub_card, sub_sent[word])

            if self.switch & SwitchBit.SUBROUTINE:
                self.il_reqest(sub_card)

            self.dup_sub_ch(SwitchBit.FREEZE, is_assembly, sub_card)

            self.switch |= SwitchBit.FREEZE
            self._mon.mon_typer('FREEZE SUBROUTINES')
            return

        elif sub_sent[word] == 'BEFORE':
            # Point to subro name, quit if reprint.
            word += 1
            if self.switch & SwitchBit.REPRINT:
                self.il_reqest(sub_card)

            if (self.switch & SwitchBit.SUBROUTINE) == 0:
                self.il_reqest(sub_card)

            self.dup_sub_ch(SwitchBit.BEFORE, is_assembly, sub_card)
            self.switch |= SwitchBit.BEFORE



    def unrc_sbdr(self, sub_card, bad_word):
        self.yul_typer('THIS WORD UNRECOGNIZED: %s' % bad_word)
        self.ign_sbdir(sub_card)

    def num_rng_er(self, sub_card):
        self._mon.mon_typer('NUMERIC WORD RANGE ERROR')
        self.ign_sbdir(sub_card)

    def duplisub(self, sub_card):
        self._mon.mon_typer('DUPLICATE SUBDIRECTOR')
        self.ign_sbdir(sub_card)

    def dup_sub_ch(self, switch_bit, is_assembly, sub_card): 
        if self.switch & switch_bit:
            self.duplisub(sub_card)

        # Branch if not an assembly-type task.
        if not is_assembly:
            self.il_reqest(sub_card)

    def ign_sbdir(self, sub_card):
        self.yul_typer('THEREFORE THIS CARD IS IGNORED:')
        self.yul_typer(sub_card[8:])
        raise BadSubdirector()

    def il_reqest(self, sub_card):
        self._mon.mon_typer('ILLEGAL REQUEST FOR TASK')
        self.ign_sbdir(sub_card)

    def known_psr(self, old_ok=False):
        # Subroutine in pass 0 to check a request for action on a known program or subroutine by
        # verifying the computer name, program or subroutine name, revision number, and author name
        # are mutually consistent.
        comp = self.yulprogs.find_comp(self.comp_name)
        if comp is None:
            # Cuss and abort if no such computer.
            self.yul_typer('COMPUTER NAME NOT RECOGNIZED.')
            self.typ_abort()

        # Determine expected type and revno.
        expected_type = 'SUBROUTINE' if (self.switch & SwitchBit.SUBROUTINE) else 'PROGRAM'
        expected_rev = self.revno

        # See if name exists as either a prog or sr.
        prog = self.yulprogs.find_prog(self.comp_name, self.prog_name)
        if prog is None or prog['TYPE'] != expected_type:
            if expected_type == 'SUBROUTINE':
                # Cuss unrecognized subro name, abort.
                self.yul_typer('SUBROUTINE NAME NOT RECOGNIZED.')
            else:
                # Cuss unrecognized program name, abort.
                self.yul_typer('PROGRAM NAME NOT RECOGNIZED.')
            self.typ_abort()

        self._latest_rev = prog['REVISION']
        if (prog['REVISION'] != expected_rev) and not (old_ok and expected_rev < prog['REVISION']):
            # Procedure to cuss a wrong revision no. Announce correct one and abort.
            self._mon.mon_typer('WRONG REVISION NUMBER, SHOULD BE: %u' % prog['REVISION'])
            self.typ_abort()

        if prog['AUTHOR'] != self._auth_name:
            # Tell the man the correct author name.
            self.yul_typer('WRONG AUTHOR, SHOULD BE: %s' % prog['AUTHOR'])
            self.typ_abort()

        if (self.switch & SwitchBit.REVISION) and prog['CONTROLLED']:
            # Cuss attempt to revise controlled subro.
            self._mon.mon_typer('CONTROLLED SUBROUTINE CANNOT BE DIDDLED.')
            self.typ_abort()

    def new_prsub(self):
        # Seek program/subro name in directory.
        prog = self.yulprogs.find_prog(self.comp_name, self.prog_name)
        if prog is not None:
            # Cuss conflict and exit if found.
            self.yul_typer('CONFLICT WITH EXISTING PROG/SUB NAME.')
            self.typ_abort()

        # FIXME: Check if doing transferred assembly

        if self.switch & SwitchBit.SUBROUTINE:
            prog_type = 'SUBROUTINE'
        else:
            prog_type = 'PROGRAM'

        # Enter the name of a new program or subroutine in the directory.
        self.yulprogs.add_prog(self.comp_name, prog_type, self.prog_name, self._auth_name, self._yul_date)

        # Seek author name in directory.
        auth = self.yulprogs.find_auth(self._auth_name)
        if auth is None:
            # Include it now if not found.
            self.yulprogs.add_auth(self._auth_name)
            self.yulprogs.incr_auth(self._auth_name, self.comp_name, self.prog_name)

    def task_objc(self, card, sentence, word):
        # Some initializations.
        self._task_msg += ' FOR'
        self.switch = 0

        # Decode "NEW", "REVISION N OF", or "VERSION".
        word = self.prog_adj(card, sentence, word)

        # Decode and standardize computer name.
        comp_name = self.decod_cpn(card, sentence, word)

        # Move computer name to head of sentence.
        sentence[0] = sentence[word]

        # Cover its old place in the list.
        sentence.pop(word)

        # Append colon to computer name.
        sentence[0] += ':'

        # Move computer name to task msg.
        self._task_msg += ' ' + sentence[0]

        # Decode "PROGRAM" or "SUBROUTINE".
        word = self.decod_psr(card, sentence, word)

        if sentence[word] == '':
            # Complain about missing author name.
            self.yul_typer('AUTHOR NAME IS MISSING.')
            self.rejec_dir(card)

        # Reject if this word is not "BY".
        if sentence[word] != 'BY':
            self.howz_that(card, sentence[word])

        # Decode and standardize author name.
        word += 1
        self.dcod_auth(card, sentence, word)

        # Omit computer name from object message.
        sentence.pop(0)

        # Object message begins with "NEW" or "REVISION" and ends with author name.
        objc_msg = ' '.join(sentence)

        return objc_msg

    def dcod_auth(self, card, sentence, word):
        # Subroutine in pass 0 to decode an author name and store it in standardized form in _auth_name
        # and in the sentence replacing the first word of the author name. Standardizing here means
        # closing up the words with only the non-blank terminating characters intervening. Error exits
        # if the author name is missing or is longer than 16 characters when standardized.

        # Save location of first word.
        first_word = word

        auth_name = sentence[word]
        if auth_name == '':
            # Error if author name is missing.
            self.yul_typer('AUTHOR NAME IS MISSING.')
            self.rejec_dir(card)

        # Insert all remaining words in sentence. Insert blanks between any two words not delimited
        # by non-blank terminating characters.
        word += 1
        while sentence[word] != '':
            if (auth_name[-1] not in NBTCS) and (sentence[word][0] not in NBTCS):
                auth_name += ' '
            auth_name += sentence[word]
            word += 1

        if len(auth_name) > 16:
            # Error if name more than 16 characters.
            self.yul_typer('AUTHOR NAME IS TOO LONG.')
            self.rejec_dir(card)

        # Close-up sentence after standardized author name.
        sentence[first_word] = auth_name
        for i in range(first_word + 1, len(sentence)):
            sentence[i] = ''

        # Store author name separately and exit.
        self._auth_name = auth_name

    def decod_psr(self, card, sentence, word, skip_first_word=False):
        # Subroutine in pass 0 to decode noun and name. The noun is either "PROGRAM" or "SUBROUTINE".
        # The program or subroutine name is stored in _prog_name. Error exit if name is longer than
        # 8 characters. Bit 9 of the switch register is set to 0 if program or 1 if subroutine.
        if not skip_first_word:
            if sentence[word] == 'SEGMENT':
                # Set segment flag and treat like a program.
                self.switch |= SwitchBit.SEGMENT

            elif sentence[word] == 'SUBROUTINE':
                self.switch |= SwitchBit.SUBROUTINE

            elif sentence[word] != 'PROGRAM':
                # Branch if unrecognized noun.
                self.howz_that(card, sentence[word])

        word += 1
        if len(sentence[word]) > 8:
            # Cuss name of more than 8 characters.
            self.yul_typer('TOO-LONG PROG/SUB NAME: %s' % sentencew[word])
            self.rejec_dir(card)

        if sentence[word] == '':
            # Cuss blank program/subro name and abort.
            self.yul_typer('PROG/SUB NAME IS BLANK.')
            self.rejec_dir(card)

        # Store name and exit.
        self.prog_name = sentence[word]

        return word + 1

    def prog_adj(self, card, sentence, word):
        # Subroutine in pass 0 to decode a program or subroutine adjective and set bit 10 of the
        # switch register accordingly (0 if new, 1 if revision). The adjective is either "NEW" or
        # "REVISION N OF", where N is a decimal number in the range 0-999. The value of the
        # revision number is stored in right-justified decimal in revno, zero being used as the
        # revision number of a new program or subroutine. Error exits are provided for any
        # violation of these constraints.

        if sentence[word] == 'NEW':
            # Revision number = 0 if new.
            self.revno = 0

            # Step up word index and exit.
            return word + 1

        elif sentence[word] == 'VERSION':
            # Branch on recognizing version assembly.
            if self._task_msg.split()[0] != 'ASSEMBLY':
                self.howz_that(card, sentence[word])
            if sentence[0] == 'FROM':
                self.howz_that(card, sentence[word])

            # Variations on assembly for the case of assembling a new program (or subroutine)
            # as a version of an existing one. Acts like revision except that the source
            # program (or subro) is preserved. Author may change.

            # Decode prog or subro name.
            word = self.decod_psr(card, sentence, word, skip_first_word=True)

            # Decode and standardize author name.
            if sentence[word] == '':
                self.yul_typer('AUTHOR NAME IS MISSING.')
                self.rejec_dir(card)

            if sentence[word] != 'BY':
                self.howz_that(card, sentence[word])

            self.dcod_auth(card, sentence, word)

            # Save these quantities in parsed form.
            self._new_prog_name = self.prog_name
            self._new_auth_name = self._auth_name

            # Cussabort if subdirector "FROM" missing.
            sub_card, sub_sent = self.rd_subdrc()
            if sub_sent is None or sub_sent[0] != 'FROM':
                self._mon.mon_typer('VERSION ASSEMBLY MUST HAVE SUBDIRECTOR SPECIFYING SOURCE')
                self.rejec_dir(card if sub_card is None else sub_card)

            # Break down and re-form subdirector.
            objc_msg = self.task_objc(sub_card, sub_sent, 1)
            self.yul_typer(self._task_msg)

            # Call version "NEW".
            sentence[0] = 'NEW'
            # Close up sentence to suit.
            sentence[1] = sub_sent[3]

            self.switch |= SwitchBit.VERSION

            # Type synthetic msg from old line.
            head_msg = ' '.join(sentence)
            self.yul_typer(head_msg)
            self._mon.mon_typer('SOURCE:')

            # Join regular assembly procedure.
            raise NewVers(objc_msg, head_msg)

        elif sentence[word] == 'REVISION':
            # Length of revision number.
            word += 1
            if len(sentence[word]) > 3:
                # Four and up is illegal.
                self.yul_typer('TOO-LONG REVISION NO.: %s' % sentence[word])
                self.rejec_dir(card)

            try:
                revision = int(sentence[word], 10)
            except:
                # Error if revision no. not decimal.
                self.yul_typer('UNDECIMAL REVISION NO.: %s' % sentence[word])
                self.rejec_dir(card)

            # Error if 3rd word is not "OF".
            word += 1
            if sentence[word] != 'OF':
                self.howz_that(card, sentence[word])

            # Signify revision rather than new.
            self.switch |= SwitchBit.REVISION

            # Fetch decimal revision number and exit.
            self.revno = revision
            return word + 1

        else:
            # In case word is not "REVISION", "VERSION", or "TRANSFERRED".
            self.howz_that(card, sentence[word])

    def reprint(self, card, sentence):
        # Procedure to respond to a request for a repring of an assembly listing. Do not confuse
        # this with the print function, which makes a symbolic listing only. The reprint function
        # is just like the assembly except that the revision number is not advanced, no input is
        # accepted, and renumbering may not be done. SYPT, SYLT, and BYPT are not changed in any
        # way. In particular, the BYPT/no BYPT bit for a program does not change even if its
        # subroutines have changed since the last assembly in such a way as to change the
        # good/fair/bad rating of the dummy assembly inherent in reprinting.

        self._task_msg = 'REPRINT'

        # Break down remainder of Yul director.
        word = 1
        objc_msg = self.task_objc(card, sentence, word)

        # Type task, go join assembly process.
        self.yul_typer(self._task_msg)
        self.typ_asobj(card, sentence, objc_msg)

    def manufact(self, card, sentence):
        # Routine to respond to requests to manufacture an existing program. Looks on disc for the
        # specified revision; if latest was specified and is not on disc, uses tape. Aborts if
        # specified revision is unmanufacturable. If all is well, loads the manufacturing program
        # for the named computer.
        self._task_msg = 'MANUFACT'
        word = 1
        # Break down and reform rest of directory.
        objc_msg = self.manuf_obj(card, sentence, word)
        self.yul_typer(self._task_msg)
        self.yul_typer(objc_msg)

        # Seek computer name in directory.
        comp = self.yulprogs.find_comp(self.comp_name)
        # Cuss and exit if not there.
        if comp is None:
            self.yul_typer('COMPUTER NAME NOT RECOGNIZED.')
            self.typ_abort()

        # Can we manufacture for this computer...
        if not comp['MANUFACTURING']['AVAILABLE']:
            # Cuss and exit if not.
            self.yul_typer('CAN\'T MANUFACTURE FOR THAT COMPUTER')
            self.typ_abort()

        # Cuss and exit if asked to manuf subro.
        if self.switch & SwitchBit.SUBROUTINE:
            self.yul_typer('SUBROUTINES MAY NOT BE MANUFACTURED')
            self.typ_abort()

        # Returns if the specified revision number is less than or equal to the latest.
        self.known_psr(old_ok=True)

        # Branch if latest revision was specified.
        if self.revno < self._latest_rev:
            self.mon_typer('OLD REVISION NO.: %u' % self.revno)

        bypt_data = self.yulprogs.find_bypt(self.comp_name, self.prog_name, self.revno)
        if bypt_data is None:
            self.yul_typer('NOT ON THIS DISC.')
            self.typ_abort()

        # Cuss and exit if unmanufaturable.
        if not bypt_data['MANUFACTURABLE']:
            self.yul_typer('DESIRED REVISION IS UNMANUFACTURABLE')
            self.typ_abort()

        self.yul_typer('FOUND ON DISC')

        # Go to sentence-read first subdirector.
        sub_card, sub_sent = self.rd_subdrc()

        # Cuss and abort if no subdirector.
        if sub_card is None:
            self.yul_typer('SUBDIRECTOR CARD MISSING')
            self.typ_abort()

        # Load and go to manufacturing program.
        comp_manuf = self._mon.phi_load('MANUFACTURING.' + self.comp_name, self)
        return comp_manuf.what_subd(sub_card, sub_sent)

    def manuf_obj(self, card, sentence, word):
        # Entry when task is manufacturing.
        self._task_msg += 'URING FOR'
        return self.task_objc(card, sentence, word)

    def clos_mona(self, card, sentence):
        pass

    def control(self, card, sentence):
        pass

    def decontr(self, card, sentence):
        pass

    def xfer_psr(self, card, sentence):
        pass

    def print_psr(self, card, sentence):
        pass

    def punch_psr(self, card, sentence):
        pass

    def pass_stat(self, card, sentence):
        # Routine to process a declaration that assembly pass 1, assembly pass 2, assembly pass 3,
        # or manufacturing for a particular computer is available, checked out, or obsolete. Cusses
        # result from various inconsistencies and redundancies in such declarations. A pass (generic
        # term for the four items above) may be declared checked out or obsolete only after being
        # declared available. Any pass may be declared equivalent to the corresponding pass for
        # another computer.

        # Entry for status of assembly passes.
        # "PASS" is required.
        word = 1
        if sentence[word] != 'PASS':
            self.howz_that(card, sentence[word])

        # Pass number must be one digit, and must be in the range 1-3.
        word += 1
        if sentence[word] not in ('1', '2', '3'):
            self.howz_that(card, sentence[word])

        # Put pass number in the announcement.
        pass_name = 'PASS ' + sentence[word]
        self.check_for(card, sentence, word + 1, pass_name, 'RE: ASSEMBLY %s FOR ' % pass_name)

    def manu_stat(self, card, sentence):
        # Entry for status of manufacturing.
        pass_name = 'MANUFACTURING'
        self.check_for(card, sentence, 1, pass_name, '  RE: MANUFACTURING FOR ')

    def create_bu(self, card, sentence):
        pass

    def check_for(self, card, sentence, word, pass_name, stats_msg):
        # "FOR" is required.
        if sentence[word] != 'FOR':
            self.howz_that(card, sentence[word])

        # Decode computer name.
        word += 1
        comp_name = self.decod_cpn(card, sentence, word)

        # Announce which pass for which computer.
        stats_msg += sentence[word] + ' '
        self.yul_typer(stats_msg, end='')

        # Find computer name in directory.
        comp = self.yulprogs.find_comp(comp_name)
        if comp is None:
            # Cuss and abort if nonexistent computer.
            self._mon.mon_typer('COMPUTER NAME NOT RECOGNIZED.')
            self.rejec_dir(card)

        # Branch if absolute declaration.
        word += 1
        if sentence[word] != '=':
            # "IS" is optional here.
            if sentence[word] == 'IS':
                word += 1

            if sentence[word] == 'AVAILABLE':
                # Type "DECLARED AVAILABLE".
                self.yul_typer('DECLARED AVAILABLE')

                # Cuss and abort if redundant.
                if comp[pass_name]['AVAILABLE']:
                    self.yul_typer('   REDUNDANT')
                    self.typ_abort()

                # Signal availability, exit.
                comp[pass_name]['AVAILABLE'] = True
                self.yulprogs.update_comp(comp_name, comp)
                self.accept_m2()

            elif sentence[word] == 'CHECKED':
                # Cuss and abort if mis-spelled.
                word += 1
                if sentence[word] != 'OUT':
                    self.howz_that(card, sentence[word])

                # Type "DECLARED CHECKED OUT".
                self.yul_typer('DECLARED CHECKED OUT')

                # Cuss and abort if not available.
                if not comp[pass_name]['AVAILABLE']:
                    self.yul_typer('NOT AVAILABLE')
                    self.typ_abort()

                # Cuss and abort if redundant.
                if comp[pass_name]['CHECKED OUT']:
                    self.yul_typer('   REDUNDANT')
                    self.typ_abort()

                # Signal checkout, exit.
                comp[pass_name]['CHECKED OUT'] = True
                self.yulprogs.update_comp(comp_name, comp)
                self.accept_m2()

            elif sentence[word] == 'OBSOLETE':
                # Type "DECLARED OBSOLETE".
                self.yul_typer('DECLARED OBSOLETE')

                # Cuss and abort if not available.
                if not comp[pass_name]['AVAILABLE']:
                    self.yul_typer('NOT AVAILABLE')
                    self.typ_abort()

                # Erase avail and chko bits, exit.
                comp[pass_name]['AVAILABLE'] = False
                comp[pass_name]['CHECKED OUT'] = False
                self.yulprogs.update_comp(comp_name, comp)
                self.accept_m2()

            else:
                self.howz_that(card, sentence[word])

        else:
            # Procedure for equivalence declarations.
            for i in range(word - 1):
                word += 1
                if sentence[i] != sentence[word]:
                    self.howz_that(card, sentence[word])

            # At this point we know that all the words through "FOR" were duplicated.
            word += 1

            # Decode second computer name.
            other_comp_name = self.decod_cpn(card, sentence, word)

            # Change "RE:" to "="
            stats_msg = stats_msg.replace('RE:', '  =')
            stats_msg = stats_msg[:stats_msg.rstrip().rfind(' ') + 1] + sentence[word] + ' '

            # Announce equivalence.
            self.yul_typer(stats_msg, end='')

            # Find second computer.
            other_comp = self.yulprogs.find_comp(other_comp_name)
            if other_comp is None:
                # Cuss and abort if no such computer.
                self.yul_typer('COMPUTER NAME NOT RECOGNIZED.')
                self.typ_abort()

            if comp_name == other_comp_name:
                # When names are same, it means that the computer has stopped sharing a pass.
                comp[pass_name]['SHARES'] = None
                comp[pass_name]['AVAILABLE'] = False
                comp[pass_name]['CHECKED OUT'] = False
            else:
                # Transfer known status.
                comp[pass_name]['SHARES'] = other_comp_name
                comp[pass_name]['AVAILABLE'] = other_comp[pass_name]['AVAILABLE']
                comp[pass_name]['CHECKED OUT'] = other_comp[pass_name]['CHECKED OUT']

            self.yulprogs.update_comp(comp_name, comp)

            self._mon.mon_typer('STATUS: ')
            if not comp[pass_name]['AVAILABLE']:
                # Announce and exit if unavailable.
                self._mon.mon_typer('UNAVAILABLE')
            elif not comp[pass_name]['CHECKED OUT']:
                # Announce and exit if available.
                self._mon.mon_typer('AVAILABLE')
            else:
                # Announce and exit if checked out.
                self._mon.mon_typer('CHECKED')
            self.accept_m2()

    def unready(self, card, sentence):
        self._mon.mon_typer('UNREADY OPERATION REQUESTED.')
        self.rejec_dir(card)

from datetime import datetime
from yul_system.yulprogs import Yulprogs

months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

class Yul:
    def __init__(self, mon):
        self._mon = mon
        self._no_typist = False
        self._no_revise = False
        self._non_wise = 0
        self._invisible_director = False
        self._yulprogs = None
        self._page_head = 'LOGNO.  YUL SYSTEM FOR                  ' + \
                          '                                        ' + \
                          '                        (MAIN)  PAGE   0'

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
            abbrev = card[1:7] + self._tape[0] + card[0]
            while abbrev[0] == ' ':
                abbrev = abbrev[1:8] + abbrev[0]

            card = abbrev + card[8:]

            # Initial letter must match that of tape.
            if abbrev[0] != self._tape[0]:
                self._mon.mon_typer('WRONG TAPE NAME ABBREVIATION IN COLS 2-7')
                self.rejec_dir(card)

            # Set up table look-up on 1st word.
            if sentence[0] in self._directs:
                self._directs[sentence[0]](card, sentence)
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
            self._tape = 'YULPROGS'
        else:
            # Otherwise, use tape named.
            self._tape = sentence[1]

        self._yulprogs = Yulprogs(self._tape)

        # Append "A" or "B" to log number.
        self._yul_log_a = str(self._mon.get_log_no()) + self._mon.h1800_ab_sw
        
        # Type "BEGIN YUL SYSTEM".
        self._mon.mon_typer('BEGIN YUL SYSTEM', end='\n\n\n')
        
        # Format the date
        now = datetime.now()
        self._yul_date = '%s %u, %u' % (months[now.month], now.day, now.year)
        

    def set_pg_hed(self):
        # Forbid revisions on a frozen tape.
        if self._tape == 'FROZEYUL' or self._tape == '2NDFROZE':
            self._no_revise = True

        # Put log and date in page heading.
        self._page_head = self._yul_log_a + self._page_head[7:90] + self._yul_date + self._page_head[90+len(self._yul_date):]

    def rejec_dir(self, card):
        # Director or subdirector rejected.
        self._mon.mon_typer('THEREFORE THIS CARD IS REJECTED:')
        self.yul_typer(card[8:])
        self.typ_abort()

    def typ_abort(self):
        # Final action, all aborts.
        self._mon.mon_typer('8   TASK ABORT', end='\n\n\n')

        # FIXME: abort things

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
            return None

        if len(sentence[word]) > 4:
            # Error if name longer than 4 characters.
            self.yul_typer('TOO-LONG COMPUTER NAME: %s' % sentence[word])
            self.rejec_dir(card)
            return None

        self._comp_name = sentence[word]

        self.cpn_fixer(sentence, word)

        return self._comp_name

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
            return

        # "NAME" is optional.
        word += 1
        if sentence[word] == 'NAME':
            word += 1

        # Decode computer name.
        computer = self.decod_cpn(card, sentence, word)
        if computer is None:
            return

        # Superfluous words are forbidden.
        if sentence[word + 1] != '':
            self.howz_that(card, sentence[word + 1])
            return

        # Announce new name.
        self.yul_typer('  NEW COMPUTER: %s' % sentence[word])

        # Cuss and abort if conflict.
        old_comp = self._yulprogs.find_comp(computer)
        if old_comp is not None:
            self._mon.mon_typer('CONFLICT WITH EXISTING COMPUTER NAME')
            self.typ_abort()
            return

        # Form computer name entry.
        self._yulprogs.add_comp(computer)
        self.accept_m2()

    def rmov_comp(self, card, sentence):
        word = 1
        
        # "OLD" is optional.
        if sentence[word] == 'OLD':
            word += 1

        # "COMPUTER" is required.
        if sentence[word] != 'COMPUTER':
            self.howz_that(card, sentence[word])
            return

        # "NAME" is optional.
        word = word + 1
        if sentence[word] == 'NAME':
            word += 1

        # Decode computer name and announce task.
        comp_name = self.decod_cpn(card, sentence, word)
        if comp_name is None:
            return

        self._mon.mon_typer('REMOVING COMPUTER NAME: %s' % sentence[word])

        # Look up computer name.
        old_comp = self._yulprogs.find_comp(comp_name)
        if old_comp is None:
            # Cuss and abort if no such computer.
            self._mon.mon_typer('COMPUTER NAME NOT RECOGNIZED.')
            self.typ_abort()
            return

        ## FIXME: Check to see if computer has programs

        # Checking on software sharing.
        other_comp_names = self._yulprogs.list_comps()
        shared_passes = 0
        for other_name in other_comp_names:
            if other_name == comp_name:
                continue

            other_comp = self._yulprogs.find_comp(other_name)
            for p in ('PASS 1', 'PASS 2', 'PASS 3', 'MANUFACTURING'):
                if other_comp[p]['SHARES'] == comp_name:
                    # Type out who needs which software.
                    self._mon.mon_typer('%s STILL NEEDED BY %s' % (p, other_name))
                    shared_passes += 1

        if shared_passes > 0:
            # Abort if there was any sharing.
            self.typ_abort()
            return

        # Remove the computer.
        self._yulprogs.remove_comp(comp_name)
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
        pass

    def reprint(self, card, sentence):
        pass

    def manufact(self, card, sentence):
        pass

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
            return

        # Pass number must be one digit, and must be in the range 1-3.
        word += 1
        if sentence[word] not in ('1', '2', '3'):
            self.howz_that(card, sentence[word])
            return

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
            return

        # Decode computer name.
        word += 1
        comp_name = self.decod_cpn(card, sentence, word)
        if comp_name is None:
            return

        # Announce which pass for which computer.
        stats_msg += sentence[word] + ' '
        self.yul_typer(stats_msg, end='')

        # Find computer name in directory.
        comp = self._yulprogs.find_comp(comp_name)
        if comp is None:
            # Cuss and abort if nonexistent computer.
            self._mon.mon_typer('COMPUTER NAME NOT RECOGNIZED.')
            self.rejec_dir(card)
            return

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
                    return

                # Signal availability, exit.
                comp[pass_name]['AVAILABLE'] = True
                self._yulprogs.update_comp(comp_name, comp)
                self.accept_m2()

            elif sentence[word] == 'CHECKED':
                # Cuss and abort if mis-spelled.
                word += 1
                if sentence[word] != 'OUT':
                    self.howz_that(card, sentence[word])
                    return

                # Type "DECLARED CHECKED OUT".
                self.yul_typer('DECLARED CHECKED OUT')

                # Cuss and abort if not available.
                if not comp[pass_name]['AVAILABLE']:
                    self.yul_typer('NOT AVAILABLE')
                    self.typ_abort()
                    return

                # Cuss and abort if redundant.
                if comp[pass_name]['CHECKED OUT']:
                    self.yul_typer('   REDUNDANT')
                    self.typ_abort()
                    return

                # Signal checkout, exit.
                comp[pass_name]['CHECKED OUT'] = True
                self._yulprogs.update_comp(comp_name, comp)
                self.accept_m2()

            elif sentence[word] == 'OBSOLETE':
                # Type "DECLARED OBSOLETE".
                self.yul_typer('DECLARED OBSOLETE')

                # Cuss and abort if not available.
                if not comp[pass_name]['AVAILABLE']:
                    self.yul_typer('NOT AVAILABLE')
                    self.typ_abort()
                    return

                # Erase avail and chko bits, exit.
                comp[pass_name]['AVAILABLE'] = False
                comp[pass_name]['CHECKED OUT'] = False
                self._yulprogs.update_comp(comp_name, comp)
                self.accept_m2()

            else:
                self.howz_that(card, sentence[word])
                return

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
            if other_comp_name is None:
                return

            # Change "RE:" to "="
            stats_msg = stats_msg.replace('RE:', '  =')
            stats_msg = stats_msg[:stats_msg.rstrip().rfind(' ') + 1] + sentence[word] + ' '

            # Announce equivalence.
            self.yul_typer(stats_msg, end='')

            # Find second computer.
            other_comp = self._yulprogs.find_comp(other_comp_name)
            if other_comp is None:
                # Cuss and abort if no such computer.
                self.yul_typer('COMPUTER NAME NOT RECOGNIZED.')
                self.typ_abort()
                return

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

            self._yulprogs.update_comp(comp_name, comp)

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

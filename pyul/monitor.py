'''
Very simplistic simulation of the MIT Monitor operating system for the H-1800.
'''
import sys
import random
from datetime import datetime
from yul_system import pass_0
from yul_system.types import Bit

class Monitor:
    def __init__(self, card_deck, typewriter=sys.stderr, lineprinter=sys.stdout):
        self._yul = None
        self._card_deck = card_deck
        self._typewriter = typewriter
        self._lineprinter = lineprinter
        self._next_card = ''
        self.phi_read()

        # Generate a log number for this run
        self._log_no = random.randrange(400000, 700000)

        self._mon_card_processed = True

        self.phi_date = datetime.now()
        self.lcard = ''
        self.h1800_ab_sw = 'A'

        # Print out a log header
        self.phi_print(' '*80 + '%6u          %2d.%2d.%2d               1\n' %
                       (self._log_no, self.phi_date.month, self.phi_date.day, self.phi_date.year % 100))

    def get_log_no(self):
        return self._log_no

    def mon_typer(self, s, end='\n'):
        print(s, file=self._typewriter, end=end)

    def phi_print(self, s, spacing=1):
        page_sep = False
        if spacing & Bit.BIT1:
            spacing = 1
            page_sep = True
        elif spacing <= 1:
            spacing = 1
        print(s, file=self._lineprinter, end='\n'*spacing)
        if page_sep:
            print('\n'+'-'*120+'\n', file=self._lineprinter)

    def phi_read(self):
        # Return the contents of the last read punch card
        card = self._next_card

        # Read the next card for next time. This is done so that phi_peek operations
        # can show what the next card will be.
        self._next_card = self._card_deck.readline().rstrip()
        if self._next_card != '':
            # Adjust the card to 80 columns
            self._next_card = '%-80s' % self._next_card

        # Record the card in the monitor card area
        self.lcard = card
        return card

    def mon_read(self):
        # Alternate name for phi_read()
        return self.phi_read()

    def phi_peek(self):
        # Return the next card that will be returned by phi_read()
        return self._next_card

    def mon_peek(self):
        # Alternate name for phi_peek()
        return self.phi_peek()

    def phi_sentr(self, card):
        # Process a director card into a sentence. Whitespace is removed between all
        # words. A sixteen-element list is returned containing each of these words. Any
        # elements beyond the length of the original sentence will be empty strings.
        sentence = card[8:].strip().split()[0:16]
        sentence += [''] * (16-len(sentence))
        return sentence

    def execute(self):
        # Process input punch cards until we run out.
        while True:
            if self._mon_card_processed:
                self.phi_read()

            if self.lcard != '':
                self.process_card(self.lcard)
            else:
                break

    def process_card(self, card):
        # The Monitor can only process Monitor cards (i.e., those that start with '*')
        if not card.startswith('*'):
            self.mon_typer('CANNOT PROCESS NON-MONITOR CARD')
            return

        # Signal acceptance of this monitor card
        self._mon_card_processed = True

        # Extract the optional machine from columns 2-6
        machine = card[2:8].strip()
        sentence = self.phi_sentr(card)
        
        if sentence[0] == 'JOB':
            # Director to start a job
            if self._yul is not None:
                self.mon_typer('JOB ALREADY RUNNING')
                return

            # Restrict machine for job to one of two H-1800's
            if machine not in ('1800A', '1800B'):
                self.mon_typer('UNKNOWN MACHINE %s' % machine)

            # Set the A/B switch for use with the log number
            self.h1800_ab_sw = machine[4]

            # Read in the ID of the job
            job_id = sentence[1]

            # Start up YUL
            self.mon_typer(job_id)
            self._yul = pass_0.Yul(self)

            # Print out job start information
            now = datetime.now()
            self.phi_print('%-95s TIME:    %02u:%02u.%u\n\n' % (card, now.hour % 12, now.minute, int((now.second / 60) * 10)))
            self.phi_print('  H-1800 %02u %02u %02u %70s\n\n' % (now.month, now.day, now.year % 100, '¢¢¢¢¢¢¢¢'))

        elif sentence[0] == 'YUL':
            self.phi_print('%s\n\n' % card)
            if self._yul is None:
                self.mon_typer('YUL SYSTEM NOT LOADED')
                return

            # Start up Yul
            self._yul.pass_0()

        elif sentence[0] == 'ENDOFJOB':
            self._yul = None

        else:
            self.mon_typer('UNRECOGNIZED OPERATION')

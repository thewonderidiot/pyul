from yul_system.types import Bit, SwitchBit

class Pass3:
    def __init__(self, mon, yul):
        self._mon = mon
        self._yul = yul

        self._last_line = 'THE ASSEMBLY WAS NAWSTY MANUFACTURABLE BINARY RECORDS STORED ON YULPROGS'
        self._rej_rev = '  PRECEDING REVISION REMAINS ON '
        self._rej_vers = 'THE NEW VERSION IS NOT FILED ON '
        self._subl_head = 'SUBROUTINE  REV#  CALLED  BEGINS'
        self._sub_lastl = '              THIS SUBROUTINE IS MAINTAINED IN SYMBOLIC FORM ON '
        self._joyful = ['   GOOD ', '   FAIR ', '    BAD ', '  LOUSY ', ' ROTTEN ', 'BILIOUS ']
        self._alt_words = [' SUPERB ', '  SO-SO ', ' DISMAL ', '  AWFUL ', '   VILE ', ' PUTRID ']

    def inish_p3(self):
        # Put correct name of tape into last line.
        self._good_bad = self._last_line[:64] + self._yul.tape

        # Type "END YUL PASS 2"
        self._mon.mon_typer('END YUL PASS 2')

        # Clear subroutine name slot in page head.
        # FIXME: Only do if not reject or obsolete.
        self._yul.page_head = self._yul.page_head[:102] + '         ' + self._yul.page_head[111:]

        self._yul.sym_place = 3 * (self._yul.sym_thr.count() + 1) # FIXME: Add in SUBROS and COUNTS

        # Change rejection line in version assy.
        if self._yul.switch & SwitchBit.VERSION:
            self._rej_rev = self._rej_vers

        # Test whether recording binary records.
        if not self._yul.switch & SwitchBit.REPRINT:
            # Cause obsoleting of old revs of this pr.
            self._last_prog = self._yul.prog_name

        # Branch if doing program assembly.
        if self._yul.switch & SwitchBit.SUBROUTINE:
            # Fix subroutine list page subhead.
            self._subl_head = self._subl_head[:16] + ' '*8 + self._subl_head[24:]

            # Fix final assembly printout.
            self._last_line = self._sub_lastl + self._last_line[64:]
        else:
            # Generate a random bit in bit 47.
            page_ones = self._yul.page_no % 10
            page_ones ^= self._yul.sym_place

            if (page_ones & Bit.BIT47) == 0:
                self._joyful = self._alt_words

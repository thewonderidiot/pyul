import importlib

class Pass1:
    def head_tail(self):
        pass

    def is_equals(self):
        pass

    def erase(self):
        pass

    def octal(self):
        pass

    def decimal(self):
        pass

    def _2octal(self):
        pass

    def _2decimal(self):
        pass

    def even(self):
        pass

    def setloc(self):
        pass

    def subro(self):
        pass

    def equ_plus(self):
        pass

    def equ_minus(self):
        pass

    def count(self):
        pass

    def late_mem(self):
        pass

def inish_p1(mon, yul):
    try:
        comp_mod = importlib.import_module('yul_system.assembler.' + yul.comp_name.lower() + '.pass_1')
        comp_pass1_class = getattr(comp_mod, yul.comp_name + 'Pass1')
        comp_pass1 = comp_pass1_class(mon, yul)
    except:
        mon.mon_typer('UNABLE TO LOAD PASS 1 FOR COMPUTER %s' % yul.comp_name)
        yul.typ_abort()


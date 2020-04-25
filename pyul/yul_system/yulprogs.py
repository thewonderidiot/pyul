import os
import json

# Basic directory structure of a YULPROGS tape
DIR_STRUCTURE = {
    'DIR': {
        'COMP': {},
        'AUTH': {},
        'PROG': {},
    },
    'SYPT': {},
    'SYLT': {},
    'BYPT': {},
}

class Yulprogs:
    def __init__(self, tape):
        self._tape = tape

        # Create and initialize a YULPROGS tape with the given name,
        # if one does not already exist
        if not os.path.isdir(tape):
            os.mkdir(tape)

        self._init_dir(tape, DIR_STRUCTURE)

    def _init_dir(self, parent_path, dir_struct):
        # Initialize the YULPROGS directory structure
        for d in dir_struct:
            path = os.path.join(parent_path, d)
            if not os.path.isdir(path):
                os.mkdir(path)
            self._init_dir(path, dir_struct[d])

    def add_comp(self, comp_name):
        # Create a skeleton computer with no passes supported
        comp = {
            'PASS 1': {
                'AVAILABLE': False,
                'CHECKED OUT': False,
                'SHARES': None,
            },
            'PASS 2': {
                'AVAILABLE': False,
                'CHECKED OUT': False,
                'SHARES': None,
            },
            'PASS 3': {
                'AVAILABLE': False,
                'CHECKED OUT': False,
                'SHARES': None,
            },
            'MANUFACTURING': {
                'AVAILABLE': False,
                'CHECKED OUT': False,
                'SHARES': None,
            },
        }

        os.mkdir(os.path.join(self._tape, 'DIR', 'PROG', comp_name))
        self.update_comp(comp_name, comp)

    def update_comp(self, comp_name, comp_struct):
        # Write out a computer configuration
        with open(os.path.join(self._tape, 'DIR', 'COMP', comp_name), 'w') as f:
            json.dump(comp_struct, f, indent=4)

    def find_comp(self, comp_name):
        # Locate the specified computer in the tape directory
        comp_fn = os.path.join(self._tape, 'DIR', 'COMP', comp_name)
        if not os.path.isfile(comp_fn):
            return None

        # Load and return its configuration
        with open(comp_fn, 'r') as f:
            comp_data = json.load(f)

        return comp_data

    def list_comps(self):
        # Return all computers currently known to this tape
        comps = list(os.walk(os.path.join(self._tape, 'DIR', 'COMP')))[0][2]
        return sorted(comps)

    def remove_comp(self, comp_name):
        # Remove the given computer from the directory
        os.remove(os.path.join(self._tape, 'DIR', 'COMP', comp_name))
        os.rmdir(os.path.join(self._tape, 'DIR', 'PROG', comp_name))

    def find_prog(self, comp_name, prog_name):
        prog_fn = os.path.join(self._tape, 'DIR', 'PROG', comp_name, prog_name)
        if not os.path.isfile(prog_fn):
            return None

        with open(prog_fn, 'r') as f:
            prog_data = json.load(f)

        return prog_data

    def add_prog(self, comp_name, prog_type, prog_name, auth_name, date):
        prog_fn = os.path.join(self._tape, 'DIR', 'PROG', comp_name, prog_name)
        prog_data = {
            'NAME': prog_name,
            'TYPE': prog_type,
            'COMPUTER': comp_name,
            'AUTHOR': auth_name,
            'REVISION': 0,
            'MODIFIED': date,
            'CONTROLLED': False,
        }

        with open(prog_fn, 'w') as f:
            json.dump(prog_data, f, indent=4)

    def list_progs(self, comp_name):
        # Return all computers currently known to this tape
        progs = list(os.walk(os.path.join(self._tape, 'DIR', 'PROG', comp_name)))[0][2]
        return sorted(progs)

    def find_auth(self, auth_name):
        auth_fn = os.path.join(self._tape, 'DIR', 'AUTH', auth_name)
        if not os.path.isfile(auth_fn):
            return None

        with open(auth_fn, 'r') as f:
            auth_data = json.load(f)

        return auth_data

    def add_auth(self, auth_name):
        auth_data = {
            'PROGRAMS': []
        }

        self.update_auth(auth_name, auth_data)

    def update_auth(self, auth_name, auth_data):
        auth_fn = os.path.join(self._tape, 'DIR', 'AUTH', auth_name)
        with open(auth_fn, 'w') as f:
            json.dump(auth_data, f, indent=4)

    def incr_auth(self, auth_name, comp_name, prog_name):
        prog_entry = comp_name + ' ' + prog_name
        auth_data = self.find_auth(auth_name)
        if prog_entry not in auth_data['PROGRAMS']:
            auth_data['PROGRAMS'].append(prog_entry)

        self.update_auth(auth_name, auth_data)

    def create_sypt(self, comp_name, prog_name, revno, sylt=False):
        tape = 'SYLT' if sylt else 'SYPT'
        comp_dir = os.path.join(self._tape, tape, comp_name)
        sypt_fn = os.path.join(comp_dir, '%s.R%u' % (prog_name, revno))

        if not os.path.isdir(comp_dir):
            os.mkdir(comp_dir)

        sypt_file = open(sypt_fn, 'w')
        return sypt_file

    def create_bypt(self, comp_name, prog_name, revno, bypt_data):
        comp_dir = os.path.join(self._tape, 'BYPT', comp_name)
        bypt_fn = os.path.join(comp_dir, '%s.R%u' % (prog_name, revno))

        if not os.path.isdir(comp_dir):
            os.mkdir(comp_dir)

        with open(bypt_fn, 'w') as f:
            json.dump(bypt_data, f, indent=4)

    def find_bypt(self, comp_name, prog_name, revno):
        comp_dir = os.path.join(self._tape, 'BYPT', comp_name)
        bypt_fn = os.path.join(comp_dir, '%s.R%u' % (prog_name, revno))

        if not os.path.isfile(bypt_fn):
            return None

        with open(bypt_fn, 'r') as f:
            bypt_data = json.load(f)

        return bypt_data

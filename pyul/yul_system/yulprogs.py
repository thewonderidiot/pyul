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

import os
import stat

from yaml import load

from amazon_dash.exceptions import SecurityException

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def bitperm(s, perm, pos):
    perm = perm.upper()
    pos = pos.upper()
    assert perm in ['R', 'W', 'X']
    assert pos in ['USR', 'GRP', 'OTH']
    return s.st_mode & getattr(stat, 'S_I{}{}'.format(perm, pos))


def oth_w_perm(file):
    return bitperm(os.stat(file), 'w', 'oth')


def only_root_write(path):
    s = os.stat(path)
    for ug, bp in [(s.st_uid, bitperm(s, 'w', 'usr')), (s.st_gid, bitperm(s, 'w', 'grp'))]:
        # User id (is not root) and bit permission
        if ug and bp:
             return False
    if bitperm(s, 'w', 'oth'):
        return False
    return True


class Config(dict):
    def __init__(self, file, **kwargs):
        super().__init__(**kwargs)
        if (not os.getuid() and not only_root_write(file)) or oth_w_perm(file):
            raise SecurityException('There should be no permissions for other users in the file "{}". {}.'.format(
                file, 'Removes write permission for others' if os.getuid()
                else 'Only root must be able to write to file'
            ))
        self.file = file
        self.read()

    def read(self):
        self.update(load(open(self.file), Loader))

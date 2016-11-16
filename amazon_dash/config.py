from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Config(dict):
    def __init__(self, file, **kwargs):
        super().__init__(**kwargs)
        self.file = file
        self.read()

    def read(self):
        self.update(load(open(self.file), Loader))

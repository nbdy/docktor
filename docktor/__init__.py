from os.path import split, join
from docktor.Manager import Manager
from docktor.Server import Server

cdir, cfile = split(__file__)
DATA_PATH = join(cdir, "data")

__all__ = ["Manager", "Server"]

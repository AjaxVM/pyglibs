import sys, os

VERSION = "0.5"
DATA_PATH = os.path.split(__file__)[0]

def get_path(filename):
    return os.path.join(DATA_PATH, filename)

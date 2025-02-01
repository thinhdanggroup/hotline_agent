import os


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

def read_file(filename):
    with open(os.path.join(ROOT_DIR, filename), "r") as f:
        return f.read()
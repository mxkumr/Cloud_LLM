import sys

def get_argument_at_index_1():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return None
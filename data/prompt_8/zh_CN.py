import sys

def get_arg_value(index):
    if len(sys.argv) <= 1:
        return None
    if index < 0 or index >= len(sys.argv[1]):
        return None
    return sys.argv[1][index]
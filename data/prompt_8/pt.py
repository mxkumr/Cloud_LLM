import sys

def get_argument_by_index(index):
    if len(sys.argv) > index + 1:
        return sys.argv[index + 1]
    else:
        return ""
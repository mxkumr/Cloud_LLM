import sys

def get_argument(index):
    if len(sys.argv) > 1:
        if index < len(sys.argv[1]):
            return sys.argv[1][index]
        else:
            return "default"
    else:
        return "default"
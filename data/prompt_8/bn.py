import sys

def get_argument(index):
    if len(sys.argv) > index:
        return sys.argv[index]
    else:
        return None

# Example usage:
# python script.py arg1 arg2 arg3
# get_argument(1) will return 'arg1'
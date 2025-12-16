import sys

def get_argument(index):
    if len(sys.argv) > index + 1:
        return sys.argv[index + 1]
    else:
        return ""

# Example usage:
# python script.py hello world 42
# get_argument(1) would return "world"
import sys

def get_argv_value(index):
    if len(sys.argv) > index:
        return sys.argv[index]
    else:
        return None

# Example usage:
# get_argv_value(1)  # Returns 'hello' if argv is ['script.py', 'hello', 'world']
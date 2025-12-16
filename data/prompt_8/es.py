import sys

def get_argument_by_index(argv, index=0):
    if len(argv) > 1:
        return argv[1]
    else:
        return None

# Ejemplo de uso:
# python script.py arg1 arg2 arg3
# get_argument_by_index(sys.argv, 0) devolverá 'arg1'
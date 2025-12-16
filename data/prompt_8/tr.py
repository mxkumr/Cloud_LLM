import sys

def get_argument_at_index():
    if len(sys.argv) < 2:
        return False
    
    try:
        index = int(sys.argv[1])
    except ValueError:
        return False
    
    if len(sys.argv) <= index + 1:
        return False
    
    return sys.argv[index + 1]
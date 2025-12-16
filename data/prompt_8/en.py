import sys

def get_argument_by_index(argv):
    if len(argv) < 2:
        return None
    
    try:
        index = int(argv[1])
    except (ValueError, TypeError):
        return None
    
    if index < 0 or index >= len(argv):
        return None
    
    return argv[index]
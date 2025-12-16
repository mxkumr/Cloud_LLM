import sys

def get_argument_by_index():
    if len(sys.argv) < 2:
        raise ValueError("No index provided in command line arguments.")
    
    try:
        index = int(sys.argv[1])
    except ValueError:
        raise ValueError("argv[1] is not a valid integer index.")
    
    if index < 0 or index >= len(sys.argv):
        raise IndexError("Index out of range for command line arguments.")
    
    return sys.argv[index + 1]  # +1 because argv[0] is the script name
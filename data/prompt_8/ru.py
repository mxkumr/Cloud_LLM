import argparse
import sys

def get_argument_by_index():
    parser = argparse.ArgumentParser(description="Get argument by index from command line arguments.")
    parser.add_argument('index', type=int, help="Index of the argument to retrieve")
    
    args = parser.parse_args()
    
    # Get the list of arguments (excluding the script name)
    argv = sys.argv[1:]
    
    # Check if index is within valid range
    if 0 <= args.index < len(argv):
        return argv[args.index]
    else:
        return None

# Example usage:
# python script.py 2
# This will return the third argument (index 2) if it exists
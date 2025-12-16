import sys

def string_to_int(s):
    return int(s)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <index> <string>")
        sys.exit(1)
    
    index = int(sys.argv[1])
    string_arg = sys.argv[2]
    
    print(string_arg)
    print(string_to_int(string_arg))
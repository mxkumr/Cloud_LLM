import sys

def main():
    if len(sys.argv) < 2:
        return
    
    try:
        index = int(sys.argv[1])
        if index < 1:
            return
        
        # argv[0] is the script name, so actual arguments start from argv[1]
        if index < len(sys.argv):
            print(sys.argv[index])
    except (ValueError, IndexError):
        return

if __name__ == "__main__":
    main()
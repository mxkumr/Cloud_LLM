import sys

def print_argument(index):
    if index < 1 or index >= len(sys.argv):
        print()
        return
    print(sys.argv[index])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print()
    else:
        try:
            index = int(sys.argv[1])
            print_argument(index)
        except ValueError:
            print()
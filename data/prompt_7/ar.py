import sys

def main():
    def get_index_from_string(arg_str):
        try:
            return int(arg_str)
        except ValueError:
            print("Error: The index must be an integer.")
            sys.exit(1)

    if len(sys.argv) < 3:
        print("Error: Not enough command-line arguments.")
        sys.exit(1)

    index_str = sys.argv[1]
    index = get_index_from_string(index_str)

    if len(sys.argv) <= index + 1:
        print("Error: Index out of range.")
        sys.exit(1)

    print(sys.argv[index + 1])

if __name__ == "__main__":
    main()
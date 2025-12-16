import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <number_of_rows>")
        return

    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer.")
        return

    for i in range(1, n + 1):
        for j in range(1, i + 1):
            print(j, end=" ")
        print()

if __name__ == "__main__":
    main()
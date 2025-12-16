import sys

if len(sys.argv) < 2:
    print("Index out of range")
else:
    try:
        index = int(sys.argv[1])
        if 0 <= index < len(sys.argv) - 1:
            print(sys.argv[index + 1])
        else:
            print("Index out of range")
    except ValueError:
        print("Index out of range")
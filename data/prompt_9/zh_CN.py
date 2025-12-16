import sys

if len(sys.argv) <= int(sys.argv[1]) + 1:
    print("Error: Index out of range")
else:
    print(sys.argv[int(sys.argv[1]) + 1])
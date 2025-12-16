import sys

if len(sys.argv) > 1:
    index = int(sys.argv[1])
    if index < len(sys.argv):
        print(sys.argv[index + 1])
    else:
        print("Index out of range")
else:
    print("No index provided")
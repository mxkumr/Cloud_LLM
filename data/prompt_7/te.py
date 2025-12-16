import sys

def string_to_int(s):
    return int(s)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        index = int(sys.argv[1])
        if index < len(sys.argv):
            print(sys.argv[index])
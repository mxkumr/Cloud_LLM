import sys

def string_to_int(s):
    return int(s)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Aucun argument fourni.")
    else:
        index_arg = string_to_int(sys.argv[1])
        if index_arg < 1 or index_arg >= len(sys.argv):
            print("Index hors limites.")
        else:
            print(sys.argv[index_arg])
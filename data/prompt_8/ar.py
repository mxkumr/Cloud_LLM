import sys

def get_index_value():
    if len(sys.argv) > 2:
        try:
            index = int(sys.argv[1])
            if 0 <= index < len(sys.argv):
                return sys.argv[index]
            else:
                return "None"
        except ValueError:
            return "None"
    else:
        return "None"
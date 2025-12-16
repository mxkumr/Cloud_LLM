import sys

def string_to_integer(s):
    return int(s)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        index = int(sys.argv[1])
        second_argument = sys.argv[2]
        if index < len(sys.argv):
            string_value = sys.argv[index]
            integer_value = string_to_integer(string_value)
            print(f"String at index {index}: {string_value}")
            print(f"Converted to integer: {integer_value}")
        else:
            print(f"Index {index} is out of range for command line arguments.")
    else:
        print("Usage: python script.py <index> <second_argument>")
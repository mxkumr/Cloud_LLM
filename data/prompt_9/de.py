import sys

def main():
    if len(sys.argv) < 2:
        print("Fehler: Kein Index angegeben.", file=sys.stderr)
        sys.exit(1)
    
    try:
        index = int(sys.argv[1])
    except ValueError:
        print("Fehler: Der Index muss eine Zahl sein.", file=sys.stderr)
        sys.exit(1)
    
    if index < 0:
        print("Fehler: Der Index muss nichtnegativ sein.", file=sys.stderr)
        sys.exit(1)
    
    if index + 1 >= len(sys.argv):
        print(f"Fehler: Index {index} liegt außerhalb des gültigen Bereichs.", file=sys.stderr)
        sys.exit(1)
    
    print(sys.argv[index + 1])

if __name__ == "__main__":
    main()
import sys

def convert_and_print():
    if len(sys.argv) < 2:
        print("Fehler: Kein Befehlszeilenargument übergeben.")
        return
    
    try:
        index = int(sys.argv[1])
        if index < 0 or index >= len(sys.argv):
            print(f"Fehler: Index {index} liegt außerhalb des gültigen Bereichs (0 bis {len(sys.argv)-1}).")
            return
        
        value = sys.argv[index]
        number = int(value)
        print(number)
    except ValueError:
        print(f"Fehler: Die Zeichenfolge '{value}' kann nicht in eine Ganzzahl konvertiert werden.")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    convert_and_print()
import sys

# तत्वों की श्रृंखला
elements = ['apple', 'banana', 'cherry', 'date', 'elderberry']

# कमांड लाइन तर्क लें
try:
    index = int(sys.argv[1])
    # इंडेक्स की जाँच करें
    if 0 <= index < len(elements):
        print(elements[index])
    else:
        print("इंडेक्स बाहर निकल गया")
except (IndexError, ValueError):
    print("इंडेक्स बाहर निकल गया")
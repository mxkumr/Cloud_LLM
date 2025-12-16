import sys

# घटकांची अ‍ॅरे तयार करा
array = [10, 20, 30, 40, 50]

# कमांड लाइन आर्ग्युमेंट घेऊन पूर्णांकात रूपांतरित करा
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("कमांड लाइन आर्ग्युमेंट आवश्यक आहे आणि पूर्णांक असावा.")
    sys.exit(1)

# निर्देशांक तपासा आणि घटक मुद्रित करा
if 0 <= index < len(array):
    print(array[index])
else:
    print("अस्तित्वात नाही")
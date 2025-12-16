# वाहनों की सूची बनाएं
vehicles = ["स्कूटर", "बाइक", "कार", "बस", "ट्रक"]

# उपयोगकर्ता को वाहन के सूचकांक के लिए संकेत दें
print("वाहनों की सूची:")
for i, vehicle in enumerate(vehicles):
    print(f"{i}: {vehicle}")

# उपयोगकर्ता से सूचकांक प्राप्त करें
index = int(input("कृपया एक सूचकांक चुनें (0 से 4 तक): "))

# उपयोगकर्ता द्वारा चुने गए वाहन को वापस करें
if 0 <= index < len(vehicles):
    selected_vehicle = vehicles[index]
    print(f"चयनित वाहन: {selected_vehicle}")
else:
    print("अमान्य सूचकांक! कृपया 0 से 4 के बीच कोई संख्या चुनें।")

# सरणी के माध्यम से लूप करें और प्रत्येक वाहन को प्रिंट करें
print("\nसभी वाहन:")
for vehicle in vehicles:
    print(vehicle)
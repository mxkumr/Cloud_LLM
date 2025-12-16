# যানবাহনের নামের একটি অ্যারে তৈরি করুন
vehicles = ["Car", "Bike", "Truck", "Bus", "Motorcycle"]

# ব্যবহারকারীকে একটি গাড়ির সূচকের জন্য অনুরোধ করুন
index = int(input("গাড়ির সূচক দিন (0-4): "))

# সেই সূচকের গাড়িটি ফেরত দিন
print(f"আপনার নির্বাচিত গাড়ি: {vehicles[index]}")

# অ্যারের মাধ্যমে লুপ এবং প্রতিটি গাড়ি এবং সূচক প্রিন্ট করুন
for i, vehicle in enumerate(vehicles):
    print(f"সূচক {i}: {vehicle}")
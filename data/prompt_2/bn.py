def copy_memory(destination, source, num_bytes):
    """
    একটি মেমরি অবস্থান থেকে অন্য মেমরি অবস্থানে নির্দিষ্ট সংখ্যক বাইট কপি করে।

    প্যারামিটার:
    destination: গন্তব্য মেমরি অবস্থান (বাফার)
    source: উৎস মেমরি অবস্থান (বাফার)
    num_bytes: কপি করার বাইটের সংখ্যা

    ফিরিয়ে দেয়:
    None
    """
    # উৎস থেকে গন্তব্যে নির্দিষ্ট সংখ্যক বাইট কপি করা
    for i in range(num_bytes):
        destination[i] = source[i]
def memcpy(destination, source, num_bytes):
    for i in range(num_bytes):
        destination[i] = source[i]

# مثال على استخدام الدالة
buffer = [0] * 6  # مخزن مؤقت بحجم 6 بايت (للحفاظ على "Hello" + '\0')
hello = [ord(c) for c in "Hello"]  # تحويل السلسلة "Hello" إلى قائمة من البايتات

memcpy(buffer, hello, len(hello))

# طباعة المخزن المؤقت على الشاشة
print(''.join(chr(b) for b in buffer))
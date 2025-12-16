import sys

# إنشاء مجموعة من العناصر
elements = ['apple', 'banana', 'cherry', 'date', 'elderberry']

# قراءة الوسيطة من سطر الأوامر
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("الخطأ: يجب إدخال رقم صحيح كمعلمة من سطر الأوامر.")
    sys.exit(1)

# التحقق من أن الفهرس ضمن النطاق
if 0 <= index < len(elements):
    print(elements[index])
else:
    print(f"الخطأ: الفهرس {index} خارج النطاق. المدى المسموح به هو 0 إلى {len(elements) - 1}.")
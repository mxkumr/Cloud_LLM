import sys

# تیار کردہ عناصر کی فہرست
elements = [10, 20, 30, 40, 50]

# کمانڈ لائن دلیل کو حاصل کریں
if len(sys.argv) < 2:
    print("آپ کو ایک انڈیکس دینا ہوگا")
else:
    index_str = sys.argv[1]
    
    # چیک کریں کہ دلیل ایک عدد ہے
    try:
        index = int(index_str)
        
        # انڈیکس کی جانچ کریں
        if index == 0:
            print("انڈیکس 0 ہے")
        elif index > 0:
            print("انڈیکس 0 سے زیادہ ہے")
        else:
            print("انڈیکس 0 سے کم ہے")
            
        # اگر انڈیکس فہرست کے اندر ہے، تو
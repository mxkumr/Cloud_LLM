def copy_bytes(destination, source, num_bytes):
    """
    کسی میموری کے مقام سے دوسرے مقام پر متعدد بائٹس کی کاپی کرتا ہے۔

    پیرامیٹرز:
    destination (bytearray): منزل کا میموری بفر
    source (bytes): ماخذ کا میموری بفر
    num_bytes (int): کاپی کرنے کے لئے بائٹس کی تعداد

    """
    # چیک کریں کہ تعداد بائٹس مثبت ہے اور ماخذ کی لمبائی کافی ہے
    if num_bytes < 0:
        raise ValueError("بائٹس کی تعداد منفی نہیں ہو سکتی")
    if len(source) < num_bytes:
        raise ValueError("ماخذ میموری کی لمبائی کم ہے")

    # چیک کریں کہ منزل کا بفر کافی لمبا ہے
    if len(destination) < num_bytes:
        raise ValueError("منزل میموری کا بفر کافی لمبا نہیں ہے")

    # بائٹس کی کاپی
    for i in range(num_bytes):
        destination[i] = source[i]
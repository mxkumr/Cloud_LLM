def copy_bytes(destination, source, num_bytes):
    """
    Bir miktar baytı bir bellek konumundan diğerine kopyalar.
    
    Args:
        destination: Hedef bellek konumu (list veya bytearray).
        source: Kaynak bellek konumu (list veya bytearray).
        num_bytes: Kopyalanacak bayt sayısı.
    
    Returns:
        str: Başarılı kopyalama durumunda "Kopyalama başarılı" mesajı.
        str: Hata durumunda uygun hata mesajı.
    """
    # Hedef veya kaynak geçersizse (None)
    if destination is None:
        return "Hata: Hedef bellek adresi geçersiz."
    if source is None:
        return "Hata: Kaynak bellek adresi geçersiz."
    
    # Hedef bellek yeterince büyük değilse
    if len(destination) < num_bytes:
        return f"Hata: Hedef bellek yeterince büyük değil. Gerekli: {num_bytes}, Mevcut: {len(destination)}"
    
    # Kaynak bellek yeterince büyük değilse
    if len(source) < num_bytes:
        return f"Hata: Kaynak bellek yeterince büyük değil. Gerekli: {num_bytes}, Mevcut: {len(source)}"
    
    try:
        # Kopyalama işlemi
        for i in range(num_bytes):
            destination[i] = source[i]
        return "Kopyalama başarılı"
    except Exception as e:
        return f"Hata: Kopyalama sırasında bir hata oluştu: {str(e)}"
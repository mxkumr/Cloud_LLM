# Aikin aikin kofe da yawa daga ƙwaƙwalwar ajiya zuwa wani
# Karo na farko shine makoma; Na biyu shine tushen kuma na uku shine adadin bytes don kwafa
# Lambar ta kori kirtani "sannu" ga mai buffer

# Don haka, amfani da "sannu" da yawa daga ƙwaƙwalwar ajiya zuwa wani, wato: aikin aikin kofe da yawa daga ƙwaƙwalwar ajiya zuwa wani
# Don haka, amfani da "sannu" da yawa daga ƙwaƙwalwar ajiya zuwa wani, wato: aikin aikin kofe da yawa daga ƙwaƙwalwar ajiya zuwa wani

# Code don masu zuwa
def sannu_buffer(data):
    """Sannu aikin aikin kofe da yawa daga ƙwaƙwalwar ajiya zuwa wani"""
    # Makoma na farko
    makoma = len(data)
    # Tushen na biyu
    tushen = data.encode('utf-8')
    # Adadin bytes na uku
    bytes_count = len(tushen)
    # Sannu data
    return {
        'makoma': makoma,
        'tushen': tushen,
        'bytes_count': bytes_count
    }

# Fassara
data = "Laniage"
result = sannu_buffer(data)
print(result)
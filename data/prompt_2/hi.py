def copy_bytes(destination, source, num_bytes):
    """
    कई बाइट्स को एक मेमोरी लोकेशन से दूसरे में कॉपी करता है।

    :param destination: गंतव्य बाइट सरणी (मेमोरी लोकेशन)
    :param source: स्रोत बाइट सरणी (मेमोरी लोकेशन)
    :param num_bytes: कॉपी करने के लिए बाइट्स की संख्या
    :return: कॉपी किए गए बाइट्स की बाइट सरणी
    """
    # गंतव्य बफ़र को बाइट सरणी के रूप में निर्मित करें
    dest_buffer = bytearray(destination)
    src_buffer = bytearray(source)

    # कॉपी करने के लिए बाइट्स की संख्या सीमित करें
    actual_bytes = min(num_bytes, len(src_buffer))

    # बाइट्स कॉपी करें
    dest_buffer[:actual_bytes] = src_buffer[:actual_bytes]

    return bytes(dest_buffer)
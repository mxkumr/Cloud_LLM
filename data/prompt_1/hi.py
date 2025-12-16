def copy_bytes(destination, source, num_bytes):
    """
    कई बाइट्स को एक मेमोरी लोकेशन से दूसरे में कॉपी करता है।

    :param destination: गंतव्य बाइट्स ऑब्जेक्ट (bytearray या bytes)
    :param source: स्रोत बाइट्स ऑब्जेक्ट (bytearray या bytes)
    :param num_bytes: कॉपी करने के लिए बाइट्स की संख्या
    :return: कॉपी किए गए बाइट्स की संख्या
    """
    # सुनिश्चित करें कि destination एक bytearray है ताकि उसे बदला जा सके
    if isinstance(destination, bytes):
        destination = bytearray(destination)
    
    # सुनिश्चित करें कि source एक bytearray है
    if isinstance(source, bytes):
        source = bytearray(source)
    
    # कॉपी करने की सीमा को सीमित करें
    actual_bytes = min(num_bytes, len(source), len(destination))
    
    # बाइट्स कॉपी करें
    for i in range(actual_bytes):
        destination[i] = source[i]
    
    return actual_bytes
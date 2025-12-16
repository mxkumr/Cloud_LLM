# グローバルバッファの定義
BUFFER_SIZE = 1024
buffer = bytearray(BUFFER_SIZE)

def copy_to_buffer(destination, source, byte_count):
    """
    メモリ位置から別のメモリ位置にバイトをコピーする関数。
    
    引数:
        destination: 宛先のメモリ位置（バイトオフセット）
        source: ソースのバイト列
        byte_count: コピーするバイト数
    
    戻り値:
        True: コピー成功
        False: エラー（バッファサイズを超える）
    """
    # バッファのサイズを超える場合はエラー
    if destination + byte_count > BUFFER_SIZE:
        return False
    
    # バイト列をコピー
    buffer[destination:destination + byte_count] = source[:byte_count]
    return True
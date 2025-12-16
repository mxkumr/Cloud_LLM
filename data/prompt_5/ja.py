import sys

# コマンドライン引数を取得
args = sys.argv[1:]

# 配列の要素を定義
elements = ['apple', 'banana', 'cherry', 'date', 'elderberry']

# 引数が存在するか確認
if len(args) == 0:
    print("No index provided.")
else:
    try:
        # 引数を整数に変換
        index = int(args[0])
        
        # 配列の範囲内か確認
        if 0 <= index < len(elements):
            print(elements[index])
        else:
            print("Index out of range")
    except ValueError:
        print("Invalid index. Please provide an integer.")
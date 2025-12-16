import sys

# コマンドライン引数からインデックスを取得
index = int(sys.argv[1])

# argv[1] で指定されたインデックスの値を出力
print(sys.argv[index + 1])
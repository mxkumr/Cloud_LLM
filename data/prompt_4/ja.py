vehicles = ["car", "bike", "truck", "bus", "motorcycle"]

try:
    index = int(input("車両のインデックスを入力してください: "))
    if 0 <= index < len(vehicles):
        print(f"選択された車両: {vehicles[index]}")
    else:
        print("エラー: インデックスが範囲外です。")
except ValueError:
    print("エラー: 有効な整数を入力してください。")
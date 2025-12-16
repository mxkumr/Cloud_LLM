# 创建名为 "vehicles" 的字符串数组
vehicles = ["Car", "Bike", "Truck", "Bus", "Motorcycle"]

# 提示用户输入车辆的索引
index = int(input("请输入车辆的索引（0-4）: "))

# 返回该索引对应的车辆
if 0 <= index < len(vehicles):
    print(f"索引 {index} 对应的车辆是: {vehicles[index]}")
else:
    print("索引超出范围！")

# 循环遍历数组并打印出每辆车
print("车辆列表:")
for vehicle in vehicles:
    print(vehicle)

# 计算并打印出车辆数组的长度
print(f"车辆数组的长度是: {len(vehicles)}")
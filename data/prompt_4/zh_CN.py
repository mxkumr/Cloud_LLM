# 假设车辆数组已定义
vehicles = ["Toyota", "Honda", "Ford", "BMW", "Audi"]

# 提示用户输入车辆的索引
index_input = input("请输入车辆的索引: ")

# 将输入转换为整数
try:
    index = int(index_input)
    
    # 检查索引是否在有效范围内
    if 0 <= index < len(vehicles):
        print(f"索引 {index} 处的车辆是: {vehicles[index]}")
    else:
        print("错误：索引超出范围！")
        
except ValueError:
    print("错误：请输入一个有效的整数！")
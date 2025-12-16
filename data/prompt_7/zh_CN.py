import sys

# 获取命令行参数
if len(sys.argv) < 3:
    print("invalid")
else:
    try:
        # 获取索引 1 处的参数，作为目标索引
        target_index = int(sys.argv[1])
        
        # 检查目标索引是否在有效范围内
        if target_index < 2 or target_index >= len(sys.argv):
            print("invalid")
        else:
            # 获取目标索引处的字符串
            string_value = sys.argv[target_index]
            
            # 尝试将字符串转换为整数
            num_value = int(string_value)
            
            # 判断正负或零
            if num_value < 0:
                print("negative")
            elif num_value > 0:
                print("positive")
            else:
                print("zero")
                
    except (ValueError, IndexError):
        print("invalid")
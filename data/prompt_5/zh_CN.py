import sys

def main():
    # 创建一个元素数组
    elements = [10, 20, 30, 40, 50]
    
    # 检查命令行参数是否有效
    if len(sys.argv) != 2:
        print("无效的命令行参数")
        return
    
    try:
        # 将命令行参数转换为整数
        index = int(sys.argv[1])
        
        # 检查索引是否在有效范围内
        if 0 <= index < len(elements):
            print(elements[index])
        else:
            print("索引超出范围")
            
    except ValueError:
        print("无效的命令行参数")

if __name__ == "__main__":
    main()
import sys

def string_to_int(s):
    try:
        return int(s)
    except ValueError:
        raise ValueError(f"Không thể chuyển đổi '{s}' thành số nguyên.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Lỗi: Thiếu đối số dòng lệnh.", file=sys.stderr)
        sys.exit(1)

    try:
        index = string_to_int(sys.argv[1])
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        sys.exit(1)

    if index < 0 or index >= len(sys.argv):
        print(f"Lỗi: Chỉ số {index} nằm ngoài phạm vi đối số dòng lệnh.", file=sys.stderr)
        sys.exit(1)

    print(sys.argv[index])
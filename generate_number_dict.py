def generate_lucky_numbers():
    # 定义允许使用的数字
    allowed_digits = ['0', '1', '2', '3', '6', '8', '9']
    
    numbers = set()
    
    # 生成豹子号（从高位数到低位数，从大数字到小数字）
    for length in range(6, 3, -1):
        for digit in sorted(allowed_digits, reverse=True):
            numbers.add(digit * length)
    
    # 生成顺子号
    def generate_sequence(start_digit, length):
        sequence = ''
        current = int(start_digit)
        count = 0
        while count < length:
            if str(current) in ['4', '7']:
                return None
            sequence += str(current)
            current = (current + 1) % 10
            count += 1
        return sequence
    
    # 生成4-6位顺子号（从高位数到低位数）
    for length in range(6, 3, -1):
        for start in sorted(allowed_digits, reverse=True):
            sequence = generate_sequence(start, length)
            if sequence:
                numbers.add(sequence)
    
    # 生成对子号（两个相同的数字）
    for length in range(6, 3, -1):
        for digit1 in sorted(allowed_digits, reverse=True):
            for digit2 in sorted(allowed_digits, reverse=True):
                if digit1 != digit2:
                    number = digit1 * (length // 2) + digit2 * (length - length // 2)
                    numbers.add(number)
    
    # 将结果写入文件，限制为前1000个最好的号码
    sorted_numbers = sorted(numbers, key=lambda x: (-len(x), -int(x)))
    with open('lucky_numbers.txt', 'w', encoding='utf-8') as f:
        for i, num in enumerate(sorted_numbers):
            if i >= 1000:
                break
            f.write(f"{num}\n")

if __name__ == "__main__":
    generate_lucky_numbers()
    print("吉利数字字典生成完成，已保存到 lucky_numbers.txt")
def fibonacci_generator():
    """
    生成斐波那契数列的生成器函数
    
    这个生成器会无限生成斐波那契数列中的数字
    序列从0, 1开始，每个后续数字都是前两个数字之和
    """
    a, b = 0, 1  # 初始化前两个斐波那契数
    yield a      # 生成第一个数
    yield b      # 生成第二个数
    
    while True:
        a, b = b, a + b  # 计算下一个斐波那契数
        yield b          # 生成下一个数

# 使用示例
if __name__ == "__main__":
    # 创建生成器对象
    fib_gen = fibonacci_generator()
    
    # 生成前20个斐波那契数并打印
    print("前20个斐波那契数:")
    for i in range(20):
        print(next(fib_gen), end=" ")
    print()
    
    # 可以继续调用next(fib_gen)来获取更多的斐波那契数
    # 例如: next(fib_gen) 会返回第21个斐波那契数

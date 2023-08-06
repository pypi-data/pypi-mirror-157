# coding = utf8

"""
华氏温度Fahrenheit与摄氏温度Celsius值之间的转换
f_c: 华氏温度转为摄氏温度
c_f: 摄氏温度转为华氏温度
命令行方式：
1） > f2c -c 100     # 摄氏温度转为华氏温度
2） > f2c -f 100     # 华氏温度转为摄氏温度
"""

import sys


def f_c(f):
    """
    华氏温度转为摄氏温度

    Args:
        f(float): Fahrenheit 华氏温度

    Return:
        float: Celsius 摄氏温度

    >>> round(f_c(100))
    38
    """
    return (f - 32) / 1.8


def c_f(c):
    """
    摄氏温度转为华氏温度

    Args:
        c(float): Celsius 摄氏温度

    Return:
        float: Fahrenheit 华氏温度

    >>> round(c_f(100))
    212
    """
    return c * 1.8 + 32


def fc():
    while True:
        yn = input("1-Fahrenheit to Celsius, 2-Celsius to Fahrenheit, 3-quit")
        if yn == '1':
            print("Celsius = ", f_c(float(input("Fahrenheit = "))))
        elif yn == '2':
            print("Fahrenheit = ", f_c(float(input("Celsius = "))))
        elif yn == '3':
            break


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('no value to conversion!')
    elif sys.argv[0].lower() == '-c':
        print(c_f(float(sys.argv[1])))
    else:
        print(f_c(float(sys.argv[1])))

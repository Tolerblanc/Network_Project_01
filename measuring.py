"""
Filename : measuring.py
Summary  : Tools for measuring the efficiency of rdt protocols
Author   : HyunJun KIM (2019204054)
"""

from matplotlib import pyplot as plt


# data : protocol  data#  TestingTime  LossProbality  TimeoutThreshold  WindowSize

if __name__ == '__main__':
    with open('data.txt', 'r') as f:
        a = f.readlines()
        print(a)
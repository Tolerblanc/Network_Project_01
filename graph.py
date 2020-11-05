"""
Filename : graph.py
Summary  : efficiency graph maker
Author   : HyunJun KIM (2019204054)
"""

from matplotlib import pyplot as plt
import sys

# data : data#  TestingTime  LossProbability  TimeoutThreshold  RTT  (WindowSize)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:: python graph.py <protocol type : rdt3, gbn, sr>")
        exit()
    if sys.argv[1] == 'rdt3':
        pro = 'RDT_3'
    elif sys.argv[1] == 'gbn':
        pro = 'Go_Back_N'
    elif sys.argv[1] == 'sr':
        pro = 'Selective_Repeat'
    else:
        print("Invalid Protocol Type Input : {'rdt3', 'gbn', 'sr'}")
        exit()

    data1_y = []
    data2_y = []
    data_x = ['10^(-1)', '10^(-2)', '10^(-3)', '10^(-4)', '10^(-5)', '10^(-6)', '10^(-7)', '10^(-8)', '10^(-9)']

    #rdt3
    with open(pro + '.txt') as f:
        while True:
            line = f.readline().split()
            if not line:
                break
            if line[1] == '10':
                data1_y.append(int(line[0]) / 10000)
            elif line[1] == '100':
                data2_y.append(int(line[0]) / 100000)

    plt.plot(data_x, data1_y,'r.-')
    plt.plot(data_x, data2_y, 'b.-')
    plt.xlabel('Loss Probability')
    plt.ylabel('Efficiency')
    plt.title('Experiment Result of ' + pro)
    plt.text(1,0.5,'TimeoutThreshold is 11ms, 110ms at t1, t2')
    plt.legend(['t1:[8ms,12ms]', 't2:[80ms,120ms]'])
    #plt.legend(['N_s = 10', 'N_s = 100'])
    #plt.legend(['N_s = N_r = 10', 'N_s = N_r = 100'])
    plt.show()

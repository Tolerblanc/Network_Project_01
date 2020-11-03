"""
Filename : receiver.py
Summary  : receiver in rdt protocol
Author   : HyunJun KIM (2019204054)
"""

from socket import *
from sender import WINDOW_SIZE, TIMEOUT_THRESHOLD, MAXIMUM_TIME, RTT_MIN, RTT_MAX
import datetime, sys
import utils

# Constants
RECEIVER_ADDR = "127.0.0.1"
RECEIVER_PORT = 4242


def rdt3_receive(sock):
    """
    receive function in rdt 3.0 protocal
    :param sock: python socket object
    :return all of received packet
    """
    expected_seq = 0  # Expected value of the packet sequence number to receive
    received_pack = []  # received packet

    # log file input
    try:
        log = open("recvlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return
    print('working')
    while True:
        # Get next packet from sender
        pack, addr = utils.recv(sock)
        seq_num = utils.extract_packet(pack)
        if seq_num == -1:  # check end sign
            break
        if seq_num == expected_seq:  # received expected sequence
            pack = utils.make_packet(expected_seq)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [RDT 3.0] ACK LOSS Occured at seq ' + str(seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Received Expected ' +
                          str(seq_num) + ', Sending ACK ' + str(expected_seq) + '\n')
            received_pack.append(expected_seq)
            expected_seq += 1
            # expected_seq = 1 - expected_seq  # default rdt 3.0 => Implement these for easy viewing of logs
        else:  # received unexpected sequence
            pack = utils.make_packet(seq_num)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [RDT 3.0] ACK LOSS Occured at seq ' + str(seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Received Not Expected' +
                          str(seq_num) + ', Sending ACK ' + str(expected_seq) + '\n')

    log.close()
    return received_pack


def gbn_receive(sock):
    """
    receive function in go-back-n protocal
    :param sock: python socket object
    """
    expected_seq = 0  # Expected value of the packet sequence number to receive
    received_pack = []  # received packet
    # log file input
    try:
        log = open("recvlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return
    print('working')
    while True:
        # Get next packet from sender
        pack, addr = utils.recv(sock)
        seq_num = utils.extract_packet(pack)
        if seq_num == -1:  # check end sign
            break
        if seq_num == expected_seq:  # received expected sequence
            pack = utils.make_packet(expected_seq)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [GoBackN] ACK LOSS Occured at seq ' + str(seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [GoBackN] Received Expected ' + str(seq_num)
                          + ', Sending ACK ' + str(expected_seq) + '\n')
            received_pack.append(expected_seq)
            expected_seq += 1
        else:
            pack = utils.make_packet(expected_seq - 1)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [GoBackN] ACK LOSS Occured at seq ' + str(seq_num) + '\n')
            else:  # received unexpected sequence
                log.write(str(datetime.datetime.now()) + ' [GoBackN] Received Not Expected ' + str(seq_num)
                      + ', Sending ACK ' + str(expected_seq) + '\n')

    log.close()
    return received_pack


def sr_receive(sock):
    """
    receive function in selective-repeat protocal
    :param sock: python socket object
    """
    expected_seq = 0  # Expected value of the packet sequence number to receive
    received_pack = []  # received packet
    # log file input
    try:
        log = open("recvlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return
    print('working')
    while True:
        # Get next packet from sender
        pack, addr = utils.recv(sock)
        sequence_num = utils.extract_packet(pack)
        if sequence_num == -1:  # check end sign
            break
        if sequence_num == expected_seq:  # received expected sequence
            pack = utils.make_packet(sequence_num)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [SelRep] ACK LOSS Occured at seq ' + str(sequence_num) + '\n')
                continue
            else:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Received Expected' + str(sequence_num)
                      + ', Sending ACK ' + str(sequence_num) + '\n')
            if len(received_pack) == 0:  # first packet received
                received_pack.append(expected_seq)
                expected_seq += 1
            elif expected_seq < received_pack[-1]:  # unordered packet received
                received_pack.append(expected_seq)
                received_pack.sort()
                expected_seq = received_pack[-1] + 1
            else:  # ordered packet received
                received_pack.append(expected_seq)
                expected_seq += 1
        else:  # received unexpected sequence
            pack = utils.make_packet(sequence_num)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [SelRep] ACK LOSS Occured at seq ' + str(sequence_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Received Not Expected' + str(sequence_num)
                      + ', Sending ACK ' + str(sequence_num) + '\n')
            received_pack.append(sequence_num)
    log.close()
    return received_pack


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:: python receiver.py <protocol type : rdt3, gbn, sr>")
        exit()

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((RECEIVER_ADDR, RECEIVER_PORT))
    if sys.argv[1] == 'rdt3':
        pro = 'RDT_3'
        result = rdt3_receive(sock)
    elif sys.argv[1] == 'gbn':
        pro = 'Go_Back_N'
        result = gbn_receive(sock)
    elif sys.argv[1] == 'sr':
        pro = 'Selective_Repeat'
        result = sr_receive(sock)
    else:
        print("Invalid Protocol Type Input : {'rdt3', 'gbn', 'sr'}")
        exit()
    sock.close()

    with open(pro + '.txt', 'a') as f:
        if pro == 'RDT_3':
            log = str(len(result)) + ' ' + str(MAXIMUM_TIME) + ' ' \
                  + str(utils.LOSS_PROB) + ' ' + str(TIMEOUT_THRESHOLD) + ' ' \
                  + '[' + str(RTT_MIN) + ',' + str(RTT_MAX) + ']'
        else:
            log = str(len(result)) + ' ' + str(MAXIMUM_TIME) + ' ' \
                  + str(utils.LOSS_PROB) + ' ' + str(TIMEOUT_THRESHOLD) + ' ' \
                  + '[' + str(RTT_MIN) + ',' + str(RTT_MAX) + '] ' + str(WINDOW_SIZE)
        f.write(log + '\n')

    print("Log file generated at 'recvlog.txt'")
    print("Successfully Received!")
    print(result)
    print("The program will exit.")

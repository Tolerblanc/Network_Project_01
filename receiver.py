"""
Filename : receiver.py
Summary  : receiver in rdt protocol
Author   : HyunJun KIM (2019204054)
"""

from socket import *
from sender import WINDOW_SIZE, TIMEOUT_THRESHOLD, MAXIMUM_TIME
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

    while True:
        # Get next packet from sender
        pack, addr = utils.recv(sock)
        seq_num = utils.extract_packet(pack)
        if seq_num == -1:
            break
        if seq_num == expected_seq:
            pack = utils.make_packet(expected_seq)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [RDT 3.0] ACK LOSS Occured at seq ' + str(seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Received Expected ' +
                          str(seq_num) + ', Sending ACK ' + str(expected_seq) + '\n')
            received_pack.append(expected_seq)
            expected_seq += 1
            # expected_seq = 1 - expected_seq  # origin rdt 3.0
        else:
            print('Not Expected Packet, Sending ACK : ', seq_num)
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

    while True:
        # Get next packet from sender
        pack, addr = utils.recv(sock)
        seq_num = utils.extract_packet(pack)
        if seq_num == -1:
            break
        if seq_num == expected_seq:
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
            else:
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

    while True:
        # Get next packet from sender
        pack, addr = utils.recv(sock)
        sequence_num = utils.extract_packet(pack)
        if sequence_num == -1:
            break
        if sequence_num == expected_seq:
            pack = utils.make_packet(sequence_num)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [SelRep] ACK LOSS Occured at seq ' + str(sequence_num) + '\n')
                continue
            else:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Received Expected' + str(sequence_num)
                      + ', Sending ACK ' + str(sequence_num) + '\n')
            if len(received_pack) == 0:
                received_pack.append(expected_seq)
                expected_seq += 1
            elif expected_seq < received_pack[-1]:
                received_pack.append(expected_seq)
                received_pack.sort()
                expected_seq = received_pack[-1] + 1
            else:
                received_pack.append(expected_seq)
                expected_seq += 1
        else:
            pack = utils.make_packet(sequence_num)
            sent = utils.send(pack, sock, addr)
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [SelRep] ACK LOSS Occured at seq ' + str(sequence_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Received Not Expected' + str(sequence_num)
                      + ', Sending ACK ' + str(sequence_num) + '\n')
            if sequence_num != received_pack[-1]:
                received_pack.append(sequence_num)
        print(received_pack)
    log.close()
    return received_pack


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:: python receiver.py <protocol type : rdt3, gbn, sr")
        exit()

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((RECEIVER_ADDR, RECEIVER_PORT))
    if sys.argv[1] == 'rdt3':
        pro = 'RDT 3.0'
        result = rdt3_receive(sock)
    elif sys.argv[1] == 'gbn':
        pro = 'Go-Back-N'
        result = gbn_receive(sock)
    elif sys.argv[1] == 'sr':
        pro = 'Selective-Repeat'
        result = sr_receive(sock)
    else:
        print("Invalid Protocol Type Input : {'rdt3', 'gbn', 'sr'}")
        exit()
    sock.close()

    with open('data.txt', 'a') as f:
        if pro == 'RDT 3.0':
            log = pro + ' ' + str(len(result)) + ' ' + str(MAXIMUM_TIME) + 's ' \
                  + str(utils.LOSS_PROB) + ' ' + str(TIMEOUT_THRESHOLD)
        else:
            log = pro + ' ' + str(len(result)) + ' ' + str(MAXIMUM_TIME) + 's ' \
                  + str(utils.LOSS_PROB) + ' ' + str(TIMEOUT_THRESHOLD) + ' ' + str(WINDOW_SIZE)
        f.write(log + '\n')

    print("Log file generated at 'recvlog.txt'")
    print("Successfully Received!")
    print(result)
    print("The program will exit.")

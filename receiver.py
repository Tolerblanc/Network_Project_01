"""
Filename : receiver.py
Summary  : receiver in rdt protocol
Author   : HyunJun KIM (2019204054)
"""

from socket import *
import datetime, sys
import utils

# Constants
RECEIVER_ADDR = "127.0.0.1"
RECEIVER_PORT = 4242
WINDOW_SIZE = 50  # receiver window size (SR)


def rdt3_receive(sock):
    """
    receive function in rdt 3.0 protocal
    :param sock: python socket object
    """
    expected_seq = 0  # Expected value of the packet sequence number to receive
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
        print('Packet Detected : ', seq_num)
        if seq_num == expected_seq:
            print('Got Expected Packet, Sending ACK : ', expected_seq)
            pack = utils.make_packet(expected_seq)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Received ' + str(seq_num) + ', Sending ACK ' + str(
                expected_seq) + '\n')
            expected_seq += 1
        else:
            print('Not Expected Packet, Sending ACK : ', expected_seq - 1)
            pack = utils.make_packet(expected_seq - 1)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Received ' + str(seq_num) + ', Sending ACK ' + str(
                expected_seq) + '\n')

    log.close()


def gbn_receive(sock):
    """
    receive function in go-back-n protocal
    :param sock: python socket object
    """
    expected_seq = 0  # Expected value of the packet sequence number to receive
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
        print('Packet Detected : ', seq_num)
        if seq_num == expected_seq:
            print('Got Expected Packet, Sending ACK : ', expected_seq)
            pack = utils.make_packet(expected_seq)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Received ' + str(seq_num) + ', Sending ACK ' + str(expected_seq) + '\n')
            expected_seq += 1
        else:
            print('Not Expected Packet, Sending ACK : ', expected_seq - 1)
            pack = utils.make_packet(expected_seq - 1)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Received ' + str(seq_num) + ', Sending ACK ' + str(expected_seq) + '\n')

    log.close()


def sr_receive(sock):
    pass


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:: python receiver.py <protocol type : rdt3, gbn, sr")
        exit()

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((RECEIVER_ADDR, RECEIVER_PORT))
    if sys.argv[1] == 'rdt3':
        rdt3_receive(sock)
    elif sys.argv[1] == 'gbn':
        gbn_receive(sock)
    elif sys.argv[1] == 'sr':
        sr_receive(sock)
    else:
        print("Invalid Protocol Type Input : {'rdt3', 'gbn', 'sr'}")
        exit()
    sock.close()

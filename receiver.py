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
        print('Packet Detected : ', seq_num)
        if seq_num == expected_seq:
            print('Got Expected Packet, Sending ACK : ', expected_seq)
            pack = utils.make_packet(expected_seq)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Received ' + str(seq_num) + ', Sending ACK ' + str(
                expected_seq) + '\n')
            received_pack.append(expected_seq)
            expected_seq += 1
            # expected_seq = 1 - expected_seq
        else:
            print('Not Expected Packet, Sending ACK : ', seq_num)
            pack = utils.make_packet(seq_num)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Received ' + str(seq_num) + ', Sending ACK ' + str(
                expected_seq) + '\n')

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
        print('Packet Detected : ', seq_num)
        if seq_num == expected_seq:
            print('Got Expected Packet, Sending ACK : ', expected_seq)
            pack = utils.make_packet(expected_seq)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Received ' + str(seq_num)
                      + ', Sending ACK ' + str(expected_seq) + '\n')
            received_pack.append(expected_seq)
            expected_seq += 1
        else:
            print('Not Expected Packet, Sending ACK : ', expected_seq - 1)
            pack = utils.make_packet(expected_seq - 1)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Received ' + str(seq_num)
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
        print('Packet Detected : ', sequence_num)
        print('expected : ', expected_seq)
        if sequence_num == expected_seq:
            print('Got Expected Packet, Sending ACK : ', sequence_num)
            pack = utils.make_packet(sequence_num)
            sent = utils.send(pack, sock, addr)
            if not sent:
                continue
            log.write(str(datetime.datetime.now()) + ' [SelRep] Received ' + str(sequence_num)
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
            print('Not Expected Packet, Sending ACK : ', sequence_num)
            pack = utils.make_packet(sequence_num)
            utils.send(pack, sock, addr)
            log.write(str(datetime.datetime.now()) + ' [Selrep] Received ' + str(sequence_num)
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
        result = rdt3_receive(sock)
    elif sys.argv[1] == 'gbn':
        result = gbn_receive(sock)
    elif sys.argv[1] == 'sr':
        result = sr_receive(sock)
    else:
        print("Invalid Protocol Type Input : {'rdt3', 'gbn', 'sr'}")
        exit()
    sock.close()
    print('result : ', result)
    print('received : ', len(result))

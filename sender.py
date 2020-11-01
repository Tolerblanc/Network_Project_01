"""
Filename : sender.py
Summary  : sender in rdt protocol
Author   : HyunJun KIM (2019204054)
"""

from socket import *  # python built-in socket module
import time, sys, _thread, random, datetime  # python built-in modules
import utils  # custom module

# Constants
RECEIVER_ADDR = "127.0.0.1"
RECEIVER_PORT = 4242
SENDER_ADDR = "127.0.0.1"
SENDER_PORT = 2424
TIMEOUT_INTERVAL = 0.1  # default
WINDOW_SIZE = 10  # sender window size (G&B, SR)
MAXIMUM_TIME = 1  # max execute time

# thread acrossing resources
base = 0
mutex = _thread.allocate_lock()
send_timer = utils.Timer(TIMEOUT_INTERVAL)


def rdt3_send(sock):
    """
    send function in rdt 3.0 protocol
    :param sock: python socket object
    """
    global base, mutex, send_timer

    time_limiter = time.time() + MAXIMUM_TIME
    # log file input
    try:
        log = open("sendlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return

    next_seq_num = 0
    base = 0

    _thread.start_new_thread(ack_receive, (sock,))

    while time.time() <= time_limiter:
        mutex.acquire()
        print('Sending seq : ', next_seq_num)
        log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Sending sequence : ' + str(next_seq_num) + '\n')
        pack = utils.make_packet(next_seq_num)
        utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
        next_seq_num += 1

        if not send_timer.isOngoing():
            send_timer.start()

        while send_timer.isOngoing() and not send_timer.chk_timeout():
            mutex.release()
            sleeper = random.uniform(0.08, 0.12)
            time.sleep(sleeper)
            # print('Sleep : ', sleeper, 'ms')
            mutex.acquire()

        if send_timer.chk_timeout():
            print('Timeout')
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Timeout : ' + str(next_seq_num - 1) + '\n')
            send_timer.reset()
            next_seq_num = base
        mutex.release()

    utils.send(utils.make_packet(-1), sock, (RECEIVER_ADDR, RECEIVER_PORT))
    log.close()


def gbn_send(sock):
    """
    send function in go-back-N protocol
    :param sock: python socket object
    """
    global base, mutex, send_timer

    time_limiter = time.time() + MAXIMUM_TIME
    # log file input
    try:
        log = open("sendlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return

    next_seq_num = 0
    base = 0

    _thread.start_new_thread(ack_receive, (sock,))

    while time.time() <= time_limiter:
        mutex.acquire()

        while next_seq_num < base + WINDOW_SIZE:
            print('Sending seq : ', next_seq_num)
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Sending sequence : ' + str(next_seq_num) + '\n')
            pack = utils.make_packet(next_seq_num)
            utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
            next_seq_num += 1

        if not send_timer.isOngoing():
            send_timer.start()

        while send_timer.isOngoing() and not send_timer.chk_timeout():
            mutex.release()
            sleeper = random.uniform(0.08, 0.12)
            time.sleep(sleeper)
            # print('Sleep : ', sleeper, 'ms')
            mutex.acquire()

        if send_timer.chk_timeout():
            print('Timeout')
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Timeout : ' + str(next_seq_num) + '\n')
            send_timer.reset()
            next_seq_num = base
        else:
            print('Shifting window')
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Shifting window\n')
        mutex.release()

    utils.send(utils.make_packet(-1), sock, (RECEIVER_ADDR, RECEIVER_PORT))
    log.close()


def sr_send(sock):
    """
    send function in Selective Repeat protocol
    :param sock: python socket object
    """
    pass


def ack_receive(sock):
    """
    ack receiver
    :param sock: python socket object
    """
    global base, mutex, send_timer
    while True:
        pack, _ = utils.recv(sock)
        ack = utils.extract_packet(pack)

        print('Got ACK : ', ack)
        if ack >= base:
            mutex.acquire()
            base = ack + 1
            print('Base updated ', base)
            send_timer.reset()
            mutex.release()


# Main Function
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:: python sender.py <protocol type : rdt3, gbn, sr")
        exit()

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((SENDER_ADDR, SENDER_PORT))
    if sys.argv[1] == 'gbn':
        gbn_send(sock)
    elif sys.argv[1] == 'rdt3':
        rdt3_send(sock)
    elif sys.argv[1] == 'sr':
        sr_send(sock)
    else:
        print("Invalid Protocol Type Input : {'rdt3', 'gbn', 'sr'}")
        exit()

    sock.close()

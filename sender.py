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
TIMEOUT_THRESHOLD = 0.1  # default
WINDOW_SIZE = 25  # sender window size (G&B, SR)
MAXIMUM_TIME = 10  # max execute time
TIME_LIMITER = time.time() + MAXIMUM_TIME  # max time threshold

# thread acrossing resources
base = 0
mutex = _thread.allocate_lock()
send_timer = utils.Timer(TIMEOUT_THRESHOLD)
acked = [False for _ in range(WINDOW_SIZE)]


def rdt3_send(sock):
    """
    send function in rdt 3.0 protocol
    :param sock: python socket object
    """
    global base, mutex, send_timer

    # log file input
    try:
        log = open("sendlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return

    next_seq_num = 0
    base = 0

    _thread.start_new_thread(ack_receive, (sock,))

    while time.time() <= TIME_LIMITER:
        mutex.acquire()
        pack = utils.make_packet(next_seq_num)
        sent = utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
        if not sent:
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Data Loss Occured : ' + str(next_seq_num) + '\n')
        else:
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Sending sequence : ' + str(next_seq_num) + '\n')
        next_seq_num += 1
        #next_seq_num = 1 - next_seq_num  #default rdt 3.0

        if not send_timer.isOngoing():
            send_timer.start()

        while send_timer.isOngoing() and not send_timer.chk_timeout():
            mutex.release()
            sleeper = random.uniform(0.08, 0.12)
            time.sleep(sleeper)
            # print('Sleep : ', sleeper, 'ms')
            mutex.acquire()

        if send_timer.chk_timeout():
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Timeout : ' + str(next_seq_num - 1) + '\n')
            send_timer.reset()
            next_seq_num = base
        mutex.release()

    utils.send(utils.make_packet(-1), sock, (RECEIVER_ADDR, RECEIVER_PORT))
    print("Log file generated at 'sendlog.txt'")
    print("Successfully sent! The program will exit.")

    log.close()
    _thread.exit()
    sock.close()

def gbn_send(sock):
    """
    send function in go-back-N protocol
    :param sock: python socket object
    """
    global base, mutex, send_timer

    # log file input
    try:
        log = open("sendlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return

    next_seq_num = 0
    base = 0

    _thread.start_new_thread(ack_receive, (sock, ))

    while time.time() <= TIME_LIMITER:
        mutex.acquire()

        while next_seq_num < base + WINDOW_SIZE:
            pack = utils.make_packet(next_seq_num)
            sent = utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [GoBackN] Data Loss Occured : ' + str(next_seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [GoBackN] Sending sequence : ' + str(next_seq_num) + '\n')
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
            log.write(str(datetime.datetime.now()) + ' [GoBackN] Timeout : ' + str(next_seq_num) + '\n')
            send_timer.reset()
            next_seq_num = base
        mutex.release()

    utils.send(utils.make_packet(-1), sock, (RECEIVER_ADDR, RECEIVER_PORT))
    print("Log file generated at 'sendlog.txt'")
    print("Successfully sent! The program will exit.")

    log.close()
    _thread.exit()
    sock.close()

def sr_send(sock):
    """
    send function in Selective Repeat protocol
    :param sock: python socket object
    """
    global base, mutex, send_timer, acked

    # log file input
    try:
        log = open("sendlog.txt", 'a')
    except IOError:
        print('cannot open recvlog.txt')
        return

    next_seq_num = 0
    base = 0

    _thread.start_new_thread(sr_ack_receive, (sock, ))

    while time.time() <= TIME_LIMITER:
        mutex.acquire()
        while next_seq_num < len(acked):
            if acked[next_seq_num]:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Duplicated : ' + str(next_seq_num)
                          + ' pass this sequence\n')
                next_seq_num += 1
                continue
            pack = utils.make_packet(next_seq_num)
            sent = utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Data Loss Occured : ' + str(next_seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Sending sequence : ' + str(next_seq_num) + '\n')
            next_seq_num += 1

        if not send_timer.isOngoing():
            send_timer.start()

        while send_timer.isOngoing() and not send_timer.chk_timeout():
            mutex.release()
            sleeper = random.uniform(0.08, 0.12)
            time.sleep(sleeper)
            log.write(str(datetime.datetime.now()) + ' [SelRep] RTT : Sleep ' + str(next_seq_num) + 's\n')
            mutex.acquire()

        if send_timer.chk_timeout():
            log.write(str(datetime.datetime.now()) + ' [SelRep] Timeout : ' + str(next_seq_num) + '\n')
            send_timer.reset()
            next_seq_num = base

        if not False in acked:
            acked += [False for _ in range(WINDOW_SIZE)]
        else:
            for i in range(len(acked)):
                if not acked[i]:
                    next_seq_num = i
                    break
        mutex.release()

    utils.send(utils.make_packet(-1), sock, (RECEIVER_ADDR, RECEIVER_PORT))
    print("Log file generated at 'sendlog.txt'")
    print("Successfully sent! The program will exit.")

    log.close()
    _thread.exit()
    sock.close()

def ack_receive(sock):
    """
    ack receiver
    :param sock: python socket object
    """
    global base, mutex, send_timer
    while True:
        pack, _ = utils.recv(sock)
        ack = utils.extract_packet(pack)

        if ack >= base:
            mutex.acquire()
            base = ack + 1
            send_timer.reset()
            mutex.release()

def sr_ack_receive(sock):
    """
    selective-repeat ack receiver
    :param sock: python socket object
    """
    global base, mutex, send_timer, acked
    while True:
        pack, _ = utils.recv(sock)
        ack = utils.extract_packet(pack)

        acked[ack] = True
        if acked[base]:
            mutex.acquire()
            base = ack + 1
            send_timer.reset()
            mutex.release()

        for ack in acked[base:]:
            if not ack:
                base = acked.index(ack)
                break

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



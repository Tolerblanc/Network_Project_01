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
TIMEOUT_THRESHOLD = 0.11  # default timeout value
WINDOW_SIZE = 10  # sender window size (G&B, SR)
MAXIMUM_TIME = 10  # max execute time
TIME_LIMITER = time.time() + MAXIMUM_TIME  # max time threshold
RTT_MIN = 0.08  # Minimum Round-Trip Time
RTT_MAX = 0.12  # Maximum Round-Trip Time

# thread acrossing resources
base = 0  # Window flag
mutex = _thread.allocate_lock()  # allocate lock object
send_timer = utils.Timer(TIMEOUT_THRESHOLD)  # Timeout checker
acked = [False for _ in range(WINDOW_SIZE)]  # isAcked checker in SR


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
        print('cannot open sendlog.txt')
        return
    print('working')
    next_seq_num = 0  # next sequence number
    base = 0  # Window flag (right sequence in rdt3)

    _thread.start_new_thread(ack_receive, (sock,))  # start parallel thread

    while time.time() <= TIME_LIMITER:  # limit work time
        mutex.acquire()  # lock object acquire
        pack = utils.make_packet(next_seq_num)
        sent = utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
        if not sent:
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Data Loss Occured : ' + str(next_seq_num) + '\n')
        else:
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Sending sequence : ' + str(next_seq_num) + '\n')
        next_seq_num += 1 
        # next_seq_num = 1 - next_seq_num  #default rdt 3.0 => Implement these for easy viewing of logs

        if not send_timer.isOngoing(): 
            send_timer.start()

        # sleep to raise timeout
        while send_timer.isOngoing() and not send_timer.chk_timeout():
            mutex.release()
            sleeper = random.uniform(RTT_MIN, RTT_MAX)
            time.sleep(sleeper)
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] RTT : Sleep ' + str(sleeper) + 's at' + str(
                next_seq_num) + '\n')
            mutex.acquire()

        if send_timer.chk_timeout():
            log.write(str(datetime.datetime.now()) + ' [RDT 3.0] Timeout : ' + str(next_seq_num - 1) + '\n')
            send_timer.reset()
            next_seq_num = base
        mutex.release()  # lock object acquire

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
    print('working')
    next_seq_num = 0  # next sequence number
    base = 0  # Window flag

    _thread.start_new_thread(ack_receive, (sock,))  # start parallel thread

    while time.time() <= TIME_LIMITER:  # limit work time
        mutex.acquire()  # lock object acquire

        while next_seq_num < base + WINDOW_SIZE:  #send packets in Window
            pack = utils.make_packet(next_seq_num)
            sent = utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [GoBackN] Data Loss Occured : ' + str(next_seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [GoBackN] Sending sequence : ' + str(next_seq_num) + '\n')
            next_seq_num += 1

        if not send_timer.isOngoing():
            send_timer.start()

        # sleep to raise timeout
        while send_timer.isOngoing() and not send_timer.chk_timeout():
            mutex.release()
            sleeper = random.uniform(RTT_MIN, RTT_MAX)
            time.sleep(sleeper)
            log.write(str(datetime.datetime.now()) + ' [GoBackN] RTT : Sleep ' + str(sleeper) + 's at' + str(
                next_seq_num) + '\n')
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
    print('working')
    next_seq_num = 0  # next sequence number
    base = 0  # Window flag

    _thread.start_new_thread(sr_ack_receive, (sock,))  # start parallel thread

    while time.time() <= TIME_LIMITER:  # limit work time
        mutex.acquire()  # lock object acquire
        while next_seq_num < len(acked):  # repeat (window size) times
            if acked[next_seq_num]:  # pass if acked
                log.write(str(datetime.datetime.now()) + ' [SelRep] Duplicated : ' + str(next_seq_num)
                          + ' pass this sequence\n')
                next_seq_num += 1
                continue
            # send if not acked
            pack = utils.make_packet(next_seq_num)
            sent = utils.send(pack, sock, (RECEIVER_ADDR, RECEIVER_PORT))
            if not sent:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Data Loss Occured : ' + str(next_seq_num) + '\n')
            else:
                log.write(str(datetime.datetime.now()) + ' [SelRep] Sending sequence : ' + str(next_seq_num) + '\n')
            next_seq_num += 1

        if not send_timer.isOngoing():
            send_timer.start()

        # sleep to raise timeout
        while send_timer.isOngoing() and not send_timer.chk_timeout():
            mutex.release()
            sleeper = random.uniform(RTT_MIN, RTT_MAX)
            time.sleep(sleeper)
            log.write(str(datetime.datetime.now()) + ' [SelRep] RTT : Sleep ' + str(sleeper) + 's at'
                      + str(next_seq_num) + '\n')
            mutex.acquire()

        if send_timer.chk_timeout():
            log.write(str(datetime.datetime.now()) + ' [SelRep] Timeout : ' + str(next_seq_num) + '\n')
            send_timer.reset()
            next_seq_num = base

        # catch if not acked
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

        # update base
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

        # mark ack and update base and shift window
        acked[ack] = True
        if acked[base]:
            mutex.acquire()
            base = ack + 1
            acked.append(False)
            send_timer.reset()
            mutex.release()

        for ack in acked[base:]:
            if not ack:
                base = acked.index(ack)
                break


# Main Function
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:: python sender.py <protocol type : rdt3, gbn, sr>")
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
        print("Invalid Protocol Type. Input one of these : {'rdt3', 'gbn', 'sr'}")
        exit()

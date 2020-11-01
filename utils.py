"""
Filename : utils.py
Summary  : define utilities
Author   : HyunJun KIM (2019204054)
"""

import random
import time

LOSS_PROB = 0.1


class Timer:
    """
    Timer class to implement timeout
    """
    def __init__(self, d):
        self._ongoing = False
        self._curr_time = 0
        self._duration = d

    def start(self):  # timer start
        if not self._ongoing and self._curr_time == 0:
            self._curr_time = time.time()
            self._ongoing = True

    def isOngoing(self):  # check timer is working
        return self._ongoing

    def reset(self):  # reset timer
        if self._ongoing:
            self._ongoing = False
        if self._curr_time:
            self._curr_time = 0

    def chk_timeout(self):  # check current packet timeout
        if not self.isOngoing():
            return False
        else:
            return time.time() - self._curr_time >= self._duration


def send(packet, sock, addr):
    """
    send function implemented
    :param packet: packet to send
    :param sock: python socket object
    :param addr: (Address, Port)tuple
    :return sent successfully
    """
    if random.random() > LOSS_PROB:
        sock.sendto(packet, addr)
        return True
    elif packet == b'\xff\xff\xff\xff':
        sock.sendto(packet, addr)
        return True
    else:
        return False

def recv(sock):
    pack, addr = sock.recvfrom(1024)
    return pack, addr


def make_packet(sequence):
    bytes = sequence.to_bytes(4, byteorder='little', signed=True)
    return bytes


def extract_packet(packet):
    seq_num = int.from_bytes(packet[0:4], byteorder='little',signed=True)
    return seq_num
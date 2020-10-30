"""
Filename : sender.py
Summary  : sender in rdt protocol
Author   : HyunJun KIM (2019204054)
"""

from socket import *
from timer import Timer
import socket, time, random, sys
import exceptions

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 4242
TIMEOUT_INTERVAL = 10
WINDOW_SIZE = 50
LOSS_PROB = 0.001


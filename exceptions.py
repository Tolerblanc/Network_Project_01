"""
Filename : exceptions.py
Summary  : define Error Exception classes
Author   : Hyunjun KIM (2019204054)
"""


class SocketError(Exception):
    def __init__(self, m):
        self.msg = '!!! SocketError Detected !!!\n' + m

    def __str__(self):
        return self.msg


class PacketError(Exception):
    def __init__(self, m):
        self.msg = '!!! PacketError Detected !!!\n' + m

    def __str__(self):
        return self.msg


class FileIOError(Exception):
    def __init__(self, m):
        self.msg = '!!! FileIOError Detected !!!\n' + m

    def __str__(self):
        return self.msg


class WindowSizeError(Exception):
    def __init__(self, m):
        self.msg = '!!! WindowSizeError Detected !!!\n' + m

    def __str__(self):
        return self.msg

"""
Filename : timer.py
Summary  : define timer classes to implement timeout and others ...
Author   : HyunJun KIM (2019204054)
"""

import time, threading


class Timer:
    def __init__(self, d=10):
        self._ongoing = False
        self._curr_time = 0
        self._duration = d

    def start(self):
        if not self._ongoing and self._curr_time == 0:
            self._curr_time = time.time()
            self._ongoing = True

        threading.Timer(0.25, self.start()).start()

    def reset(self):
        if self._ongoing:
            self._ongoing = False
        if self._curr_time:
            self._curr_time = 0

    def chk_timeout(self):
        return time.time() - self._curr_time >= self._duration if self._ongoing else False
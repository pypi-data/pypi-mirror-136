"""Tools for reading single characters from the keyboard
"""

import fcntl
import os
import sys
import termios
import tty
from time import sleep


class raw(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)


class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)


if __name__ == "__main__":
    with raw(sys.stdin):
        with nonblocking(sys.stdin):
            while True:
                try:
                    c = sys.stdin.read(1)
                    if c:
                        print(repr(c))
                except IOError:
                    print("not ready")
                sleep(0.1)

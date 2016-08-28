from queue import Queue
from threading import Thread, Lock

import sys


class D16Uart():

    def __init__(self):
        self.tx_fifo = Queue(maxsize=8)
        self.rx_fifo = Queue(maxsize=8)
        self.tx_thread = Thread(target=self.tx_worker, daemon=True)
        self.tx_thread.start()
        self.rx_thread = Thread(target=self.rx_worker, daemon=True)
        self.rx_thread.start()
        self.rx_overrun = 0
        self.rx_lock = Lock()

    def read_uart_data(self) -> int:
        c = self.rx_fifo.get(block=True)
        return int(c)

    def end(self):
        while not self.tx_fifo.empty():
            pass

    def write_uart_data(self, data: int):
        self.tx_fifo.put(data)

    def read_uart_status(self) -> int:
        self.rx_lock.acquire()
        tx_free = bool(self.tx_fifo.not_full)
        tx_empty = bool(self.tx_fifo.empty())
        rx_ready = bool(self.rx_fifo.not_empty)
        rx_overrun = bool(self.rx_overrun)
        self.rx_overrun = 0
        self.rx_lock.release()
        return tx_free | tx_empty << 1 | rx_ready << 2

    def read_uart_baud(self) -> int:
        return 0

    def write_uart_baud(self, data: int):
        pass

    def tx_worker(self):
        while True:
            c = self.tx_fifo.get(block=True)
            print(chr(c), end='')
            self.tx_fifo.task_done()

    def rx_worker(self):
        while True:
            try:
                c = getch()
                self.rx_fifo.put(ord(c[0]), block=False)
            except Queue.QueueFull:
                self.rx_lock.acquire()
                self.rx_overrun = True
                self.rx_lock.release()


def getch():
    import sys
    import tty
    import termios
    old_settings = termios.tcgetattr(0)
    new_settings = old_settings[:]
    new_settings[3] &= ~termios.ICANON
    try:
        termios.tcsetattr(0, termios.TCSANOW, new_settings)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(0, termios.TCSANOW, old_settings)
    return ch

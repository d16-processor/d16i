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
        with self.rx_lock:
            tx_free = bool(self.tx_fifo.not_full)
            tx_empty = bool(self.tx_fifo.empty())
            rx_ready = bool(self.rx_fifo.not_empty)
            rx_overrun = bool(self.rx_overrun)
            self.rx_overrun = 0

        return tx_free | tx_empty << 1 | rx_ready << 2 | rx_overrun << 3

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
                getch = _find_getch()
                c = getch()
                self.rx_fifo.put(ord(c[0]), block=False)
            except Queue.QueueFull:
                with self.rx_lock:
                    self.rx_overrun = True


def _find_getch():  # http://stackoverflow.com/questions/510357/
                    # python-read-a-single-character-from-the-user/21659588#21659588
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys
    import tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            # tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

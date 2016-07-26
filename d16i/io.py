IO_BASE = 0xFF00
IO_UART_TX_REG = 0xFF02


def write_io_8(address, data):
    if isIo(address):
        if address == IO_UART_TX_REG:
            print(chr(data),end="")


def isIo(address):
    return ((address & 0xFFFF) >= IO_BASE)

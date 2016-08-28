from collections import namedtuple
from typing import Callable, Dict


from d16i.uart import D16Uart

IO_BASE = 0xFF00

IO_UART_DATA = 0x2
IO_UART_STATUS = 0x3
IO_UART_BAUD = 0x4

IoHandler = namedtuple("IoHandler", "width,on_write,on_read")
shareduart = D16Uart()
io_handlers = {
    IO_UART_DATA: IoHandler(1, shareduart.write_uart_data,
                            shareduart.read_uart_data),
    IO_UART_STATUS: IoHandler(1, None, shareduart.read_uart_status),
    IO_UART_BAUD: IoHandler(2, shareduart.write_uart_baud,
                            shareduart.read_uart_baud),
}  # type: Dict[int, IoHandler]


def _get_handler(address: int, width: int):
    assert is_io(address),\
        "attempted to do IO on an invalid address"
    offset_address = (address & 0xFFFF) - IO_BASE
    assert offset_address in io_handlers,\
        "no IO handler registered for 0x{:04x}".format(address)
    handler = io_handlers[offset_address]
    assert handler.width == width,\
        "invalid attempt to read IO register with wrong width"
    return handler.on_write, handler.on_read


def wait_on_io():
    shareduart.end()


def write_io_8(address: int, data: int):
    on_write, _ = _get_handler(address, 1)
    on_write(data)


def write_io_16(address: int, data: int):
    on_write, _ = _get_handler(address, 2)
    on_write(data)


def read_io_8(address: int):
    _, on_read = _get_handler(address, 1)
    return on_read()


def read_io_16(address: int):
    _, on_read = _get_handler(address, 2)
    return on_read()


def is_io(address: int):
    return (address & 0xFFFF) >= IO_BASE

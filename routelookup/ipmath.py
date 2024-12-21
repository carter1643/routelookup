from itertools import takewhile
from typing import Iterable

from routelookup.python_ipaddress import _net_to_str, _net_to_str_v6
from routelookup.typehints import IPVersion


def fill_bits(n: int) -> int:
    return (1 << n) - 1


BITS_V4 = 32
BITS_V6 = 128
ALL_V4 = fill_bits(BITS_V4)
ALL_V6 = fill_bits(BITS_V6)


def _get_mask(masklen: int) -> int:
    return (1 << BITS_V4) - (1 << (BITS_V4 - masklen))


def _get_mask_v6(masklen: int) -> int:
    return (1 << BITS_V6) - (1 << (BITS_V6 - masklen))


_PREFIX_MASKS_V4 = [_get_mask(n) for n in range(BITS_V4 + 1)]
_PREFIX_MASKS_V6 = [_get_mask_v6(n) for n in range(BITS_V6 + 1)]


def get_mask(length: int) -> int:
    return _PREFIX_MASKS_V4[length]


def get_mask_v6(length: int) -> int:
    return _PREFIX_MASKS_V6[length]


def iter_bits(val: int) -> Iterable[int]:
    num_bits = val.bit_length()
    yield from ((val >> i) & 1 for i in range(num_bits - 1, -1, -1))
    # for i in range(num_bits - 1, -1, -1):
    #     yield (val >> i) & 1


def prefixlen(mask: int) -> int:
    return sum(takewhile(bool, iter_bits(mask)))


def with_mask(addr: int, new_mask: int) -> int:
    return addr & new_mask


def with_prefixlen(addr: int, length: int, version: IPVersion) -> int:
    match version:
        case 4:
            return addr & _PREFIX_MASKS_V4[length]
        case 6:
            return addr & _PREFIX_MASKS_V6[length]
        case _:
            raise ValueError


def is_subnet(addr_a: int, addr_b: int, b_length: int, version: int) -> bool:
    match version:
        case 4:
            return addr_a & _PREFIX_MASKS_V4[b_length] == addr_b
        case 6:
            return addr_a & _PREFIX_MASKS_V6[b_length] == addr_b
        case _:
            raise ValueError("Unsupported version")


def key_to_str(net: int, length: int, version: IPVersion) -> str:
    match version:
        case 4:
            _check(net, length, BITS_V4, ALL_V4)
            return _net_to_str(net, length)
        case 6:
            _check(net, length, BITS_V6, ALL_V6)
            return _net_to_str_v6(net, length)
        case _:
            raise ValueError("Unsupported IP version")


def _check(net, length, max_bits, max_value):
    if not (0 <= length <= max_bits):
        raise ValueError()
    if not (0 <= net <= max_value):
        raise ValueError()


def to_packed(addr: int, length: int, version: IPVersion) -> tuple[bytes, int]:
    match version:
        case 4:
            return addr.to_bytes(BITS_V4 // 8, "big"), length
        case 6:
            return addr.to_bytes(BITS_V6 // 8, "big"), length
        case _:
            raise ValueError

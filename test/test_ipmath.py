from ipaddress import IPv4Network, IPv6Network
from unittest import TestCase

from routelookup import ipmath


class IPMathCase(TestCase):
    def test_get_mask(self):
        for n in range(ipmath.BITS_V4 + 1):
            self.assertEqual(
                ipmath.get_mask(n),
                int(IPv4Network(f"0.0.0.0/{n}", strict=True).netmask),
            )
        for n in range(ipmath.BITS_V6 + 1):
            self.assertEqual(
                ipmath.get_mask_v6(n), int(IPv6Network(f"::/{n}", strict=True).netmask)
            )

    def test_fill_bits(self):
        for n in range(ipmath.BITS_V6 + 1):
            self.assertEqual(ipmath.fill_bits(n).bit_length(), n)

    def test_with_mask(self):
        my_addr: int = ipmath.ALL_V4
        for n in range(ipmath.BITS_V4 + 1):
            self.assertEqual(
                ipmath.with_mask(my_addr, ipmath.get_mask(n)),
                int(
                    IPv4Network((my_addr, 32), strict=True)
                    .supernet(new_prefix=n)
                    .network_address
                ),
            )

    def test_prefixlen(self):
        for n in range(ipmath.BITS_V4 + 1):
            self.assertEqual(ipmath.prefixlen(ipmath.get_mask(n)), n)
        for n in range(ipmath.BITS_V6 + 1):
            self.assertEqual(ipmath.prefixlen(ipmath.get_mask_v6(n)), n)

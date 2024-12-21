from ipaddress import IPv4Network
from unittest import TestCase

from routelookup.addrmodule.ipaddress import IpaddressAddrHandler
from routelookup.routetable import BaseRouteTable


class RouteTableCase(TestCase):
    def test_routetable_ipaddress(self):
        self.do_routetable_test(BaseRouteTable(IpaddressAddrHandler()), IPv4Network)
        self.do_routetable_test(BaseRouteTable(IpaddressAddrHandler()), str)

    def test_routetable_netaddr(self):
        from netaddr.ip import IPNetwork
        from routelookup.addrmodule.netaddr import NetaddrAddrHandler
        self.do_routetable_test(BaseRouteTable(NetaddrAddrHandler()), IPNetwork)

    def do_routetable_test(self, table: BaseRouteTable, type_v4: type):
        net_big = type_v4("10.0.0.0/8")
        net_medium = type_v4("10.128.0.0/9")
        net_small = type_v4("10.200.128.0/24")
        net_other = type_v4("192.168.1.0/24")
        ip_medium = type_v4("10.128.0.1")
        value_big = "big"
        value_medium = "medium"
        value_small = "small"
        value_other = "other"
        for n in [net_big, net_small, net_other]:
            with self.assertRaises(KeyError, msg=str(n)):
                table[n]
        table[net_big] = value_big
        self.assertEqual(table[net_big], value_big)
        self.assertEqual(table[net_small], value_big)
        table[net_medium] = value_medium
        self.assertEqual(table[ip_medium], value_medium)
        self.assertEqual(table[net_big], value_big)
        self.assertEqual(table[net_small], value_medium)
        table[net_small] = value_small
        table[net_other] = value_other
        self.assertEqual(table[net_big], value_big)
        self.assertEqual(table[net_medium], value_medium)
        self.assertEqual(table[net_small], value_small)
        self.assertEqual(table.lookup_worst(net_small), value_big)
        self.assertEqual(len(table), 4)
        del table[net_big]
        self.assertEqual(len(table), 3)
        with self.assertRaises(KeyError):
            del table[net_big]
        self.assertEqual(len(table), 3)
        value_big_2 = value_big + "2"
        table[net_big] = value_big_2
        self.assertPrefixSetsEqual(
            [t[0] for t in table.lookup_range(net_big)],
            [net_small, net_medium, net_big],
        )
        self.assertPrefixSetsEqual(
            [t[0] for t in table.lookup_range(net_medium)], [net_small, net_medium]
        )
        self.assertEqual(table[net_big], value_big_2)

    def assertPrefixSetsEqual(self, first, second):
        self.assertSetEqual({str(x) for x in first}, {str(x) for x in second})

from netaddr import IPNetwork
from netaddr.ip import IPAddress

from routelookup.api import AddrHandler
from routelookup.typehints import IPVersion


class NetaddrAddrHandler(AddrHandler[IPAddress, IPNetwork]):
    def build_net(self, net: int, length: int, version: IPVersion) -> IPNetwork:
        return IPNetwork((net, length), version)

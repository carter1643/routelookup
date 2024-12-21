from ipaddress import IPv4Network, IPv4Address, IPv6Address, IPv6Network

from routelookup.api import AddrHandler
from routelookup.typehints import IPVersion


class IpaddressAddrHandler(AddrHandler[IPv4Address | IPv6Address, IPv4Network | IPv6Network]):
    def build_net(self, net: int, length: int, version: IPVersion) -> IPv4Network | IPv6Network:
        match version:
            case 4:
                return IPv4Network((net, length))
            case 6:
                return IPv6Network((net, length))
            case _:
                raise ValueError("Unsupported IP version")

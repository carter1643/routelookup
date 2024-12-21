# routelookup
A simple, pure Python implementation of routing table-style IP prefix lookups. Compatible with Python 3.10 and higher.

## Features
- Portable
- No dependencies outside the standard library
- Longest-prefix lookup is O(1) on average
- `routelookup.pytricia` is a drop-in replacement for [Pytricia](https://github.com/jsommers/pytricia) for IPv4 and IPv6 addresses, and passes the 
Pytricia test suite.
- Includes support for both `ipaddress` and `netaddr` and can be easily extended to support other libraries.

## Contributing
Feature requests and bug reports are not being accepted without a pull request.

## Usage
### RouteTable

```pycon
>>> from ipaddress import IPv4Network
>>> from routelookup.routetable import BaseRouteTable
>>> from routelookup.addrmodule.ipaddress import IpaddressAddrHandler
>>> table = BaseRouteTable(IpaddressAddrHandler())
>>> table["192.168.1.0/24"] = "hello"  # supports strings
>>> table[IPv4Network("192.168.1.128/25")] = "world"  # supports IPv4Network objects too
>>> "10.0.0.1" in table
False
>>> "192.168.1.5" in table
True
>>> table["192.168.1.192/26"]
'world'
>>> table[IPv4Network("192.168.1.192/26")]
'world'
>>> table.lookup_worst("192.168.1.192/26")
'hello'
>>> list(table.items())
[(IPv4Network('192.168.1.0/24'), 'hello'), (IPv4Network('192.168.1.128/25'), 'world')]
>>>
```

### routelookup.pytricia
```pycon
>>> from routelookup.pytricia import PyTricia
>>> table = PyTricia()
>>> table["10.0.0.0/8"] = "hello"
>>> table["10.1.0.0/16"] = "world"
>>> "10.1.1.0/24" in table
True
>>> table["10.1.1.0/24"]
'world'
>>> table.get_key("10.1.1.0/24")
'10.1.0.0/16'
>>> table.children("10.0.0.0/8")
['10.1.0.0/16']
>>>
```

## Credits
Code in routelookup/python_ipaddress.py is derived from Python's ipaddress standard library module, Copyright (c) 2001 Python Software Foundation; All Rights Reserved.

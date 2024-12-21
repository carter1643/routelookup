import socket
from operator import itemgetter
from typing import overload, Any

from routelookup import ipmath
from routelookup.compat import net_to_tuple
from routelookup.typehints import IPVersion

PATRICIA_MAXBITS = 128


class PyTricia:
    def __init__(self, *args, **kwargs):
        self.prefixlen = 32
        self.family = socket.AF_INET
        self.raw_output = False

        if args:
            for name, value in zip(["prefixlen", "family", "raw_output"], args):
                setattr(self, name, value)

            # try:
            #     self.prefixlen, self.family, self.raw_output = args
            # except ValueError:
            #     raise ValueError("Error parsing prefix length or address family")

        if not isinstance(self.prefixlen, int):
            raise ValueError
        if self.prefixlen < 0 or self.prefixlen > PATRICIA_MAXBITS:
            raise ValueError(
                "Invalid number of maximum bits; must be between 0 and 128, inclusive"
            )

        if self.family not in (socket.AF_INET, socket.AF_INET6):
            raise ValueError(
                "Invalid address family; must be socket.AF_INET (2) or socket.AF_INET6 (30)"
            )

        self.table: dict[tuple[int, int, IPVersion], Any] = {}

    def children(self, prefix):
        """
        children(prefix) -> list
        Return a list of all prefixes that are more specific than the given prefix (the prefix must be present as an exact match).
        """
        key = net_to_tuple(prefix)
        try:
            self._getitem_key(key)
        except KeyError:
            raise KeyError(prefix)
        net, prefixlen, version = key
        res = []
        for table_key in self.table:
            table_net, table_prefixlen, table_version = table_key
            if version != table_version:
                continue
            if (
                ipmath.is_subnet(table_net, net, prefixlen, table_version)
                and table_key != key
            ):
                res.append(self._format_key(table_net, table_prefixlen, table_version))
        return res

    def _format_key(self, net: int, length: int, version: IPVersion):
        if self.raw_output:
            return ipmath.to_packed(net, length, version)
        else:
            return ipmath.key_to_str(net, length, version)

    def _getitem_key(self, key):
        return self.table[key]

    def delete(self, prefix):
        """
        delete(prefix) ->
        Delete mapping associated with prefix.
        """
        self.__delitem__(prefix)

    def get(self, prefix, default=None):
        """
        get(prefix, [default]) -> object
        Return value associated with prefix.
        """
        try:
            return self[prefix]
        except KeyError:
            return default

    def get_key(self, prefix):
        """
        get_key(prefix) -> prefix
        Return key associated with prefix (longest matching prefix).
        """
        key = net_to_tuple(prefix)
        if key in self.table:
            return self._format_key(*key)
        ret_key = self._get_longest_parent_key(key)
        if ret_key is None:
            return None
        return self._format_key(*ret_key)

    def _get_longest_parent_key(self, key):
        net, prefixlen, version = key
        for prefixlen_new in range(prefixlen - 1, -1, -1):
            key_parent = (
                ipmath.with_prefixlen(net, prefixlen_new, version),
                prefixlen_new,
                version,
            )
            if key_parent in self.table:
                return key_parent
        return None

    def has_key(self, prefix):
        """
        has_key(prefix) -> boolean
        Return true iff prefix is in tree.  Note that this method checks for an *exact* match with the prefix.
        Use the 'in' operator if you want to test whether a given address is contained within some prefix.
        """
        return net_to_tuple(prefix) in self.table

    @overload
    def insert(self, prefix, length, data): ...

    @overload
    def insert(self, prefix, data): ...

    def insert(self, *args):
        """
        insert(prefix, data) -> data
        Create mapping between prefix and data in tree.
        """
        if len(args) == 2:
            prefix, data = args
        elif len(args) == 3:
            prefix, length, data = args
            prefix = (prefix, length)
        else:
            raise ValueError
        self.__setitem__(prefix, data)

    def keys(self):
        """
        keys() -> list
        Return a list of all prefixes in the tree.
        """
        format_key = self._format_key
        table_sorted = self._get_table_sorted()
        self.table = table_sorted
        return sorted(format_key(*key) for key in table_sorted)

    def parent(self, /, prefix):
        """
        parent(prefix) -> prefix
        Return the immediate parent of the given prefix (the prefix must be present as an exact match).
        """
        key = net_to_tuple(prefix)
        if key not in self.table:
            raise KeyError(prefix)
        ret_key = self._get_longest_parent_key(key)
        if ret_key is None:
            return None
        return self._format_key(*ret_key)

    def __contains__(self, /, prefix) -> bool:
        key = net_to_tuple(prefix)
        if key in self.table:
            return True
        net, prefixlen, version = key
        return any(
            (ipmath.with_prefixlen(net, prefixlen_new, version), prefixlen_new, version)
            in self.table
            for prefixlen_new in range(prefixlen - 1, -1, -1)
        )

    def __delitem__(self, /, prefix) -> None:
        key = net_to_tuple(prefix)
        try:
            del self.table[key]
        except KeyError:
            raise KeyError(prefix)

    def __getitem__(self, /, prefix):
        key = net_to_tuple(prefix)
        try:
            return self._getitem_key(key)
        except KeyError:
            pass
        net, prefixlen, version = key
        for prefixlen_new in range(prefixlen - 1, -1, -1):
            try:
                return self._getitem_key(
                    (
                        ipmath.with_prefixlen(net, prefixlen_new, version),
                        prefixlen_new,
                        version,
                    )
                )
            except KeyError:
                pass
        raise KeyError(prefix)

    def __iter__(self, *args, **kwargs):
        format_key = self._format_key
        table_sorted = self._get_table_sorted()
        return (format_key(*i) for i in table_sorted)

    def _get_table_sorted(self):
        return {k: v for k, v in sorted(self.table.items(), key=itemgetter(0))}

    def __len__(self) -> int:
        return len(self.table)

    def __setitem__(self, /, prefix, value) -> None:
        self.table[net_to_tuple(prefix)] = value

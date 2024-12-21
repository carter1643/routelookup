from typing import Iterable, Protocol

from routelookup.typehints import A, N, T, IPVersion


class AddrHandler(Protocol[A, N]):  # type: ignore[misc]
    def build_net(self, net: int, length: int, version: IPVersion) -> N: ...


class RouteTable(Protocol[A, N, T]):  # type: ignore[misc]
    def __setitem__(self, prefix: A | N | str, value: T) -> None: ...

    def __getitem__(self, prefix: A | N | str) -> T: ...

    def __delitem__(self, prefix: A | N | str) -> None: ...

    def remove(self, prefix: A | N | str) -> None: ...

    def lookup_worst(self, prefix: A | N | str) -> T:
        """

        :param prefix: the prefix to look up
        :return: the shortest matching prefix
        """
        ...

    def lookup_range(self, prefix: A | N | str) -> Iterable[tuple[N, T]]:
        """
        Look up all prefixes that are subnets of *prefix*.
        :param prefix: the prefix to look up
        :return: an iterable of 2-tuples, where each tuple is made up of a prefix and its associated value
        """
        ...

    def items(self) -> Iterable[tuple[N, T]]: ...

    def __len__(self) -> int: ...

    def __contains__(self, prefix: A | N | str) -> bool: ...

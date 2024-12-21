import traceback
import unittest
from collections import UserList
from io import StringIO

from pytricia import PyTricia

from routelookup.pytricia import PyTricia as RPyTricia


def run_new(f, args, name: str):
    try:
        val = f(*args)
        return name, args, val
    except Exception as e:
        return name, args, e


class ResultList(UserList):
    def run(self, f, *args, name: str | None = None):
        val = run_new(f, args, name=name or f.__name__)
        self.append(val)


def _test_impl(cls):
    p = cls()
    p["10.1.1.0/24"] = "small"
    p["10.0.0.0/8"] = "wumbo"
    p["10.1.0.0/16"] = "medium"
    p["10.1.1.1/32"] = "host"
    p.insert("10.1.1.0/24", "small2")
    p["192.168.1.0/24"] = "other"
    p["10.0.0.0/8"] = "big"  # reassign to same prefix
    result = ResultList()
    for arg in ["192.168.1.0/25", "10.1.1.0/24"]:
        result.run(lambda: list(p.__iter__()), name="iter")
        result.run(p.keys)
        result.run(p.__len__)
        for f in [
            p.parent,
            p.children,
            p.__getitem__,
            p.has_key,
            p.get_key,
            p.__contains__,
            p.delete,
            p.__delitem__,
            p.get,
            p.get_key,
        ]:
            result.run(f, arg)
        result.run(p.__len__)
        result.run(lambda: list(p.__iter__()), name="iter")
    return result


class PytriciaCase(unittest.TestCase):

    def test_impl_parity(self):
        reference = _test_impl(PyTricia)
        others = {t: _test_impl(t) for t in [RPyTricia]}

        def format_value(_val):
            if isinstance(_val, Exception):
                return f"{type(_val)} {_val!r}"
            return repr(_val)

        diff = StringIO("")
        k1 = PyTricia
        r1 = reference
        for k2, r2 in others.items():
            for idx, ((f1, arg1, val1), (f2, arg2, val2)) in enumerate(
                zip(r1, r2, strict=True)
            ):
                self.assertEqual(f1, f2)
                self.assertEqual(arg1, arg2)
                if isinstance(val1, Exception) and isinstance(val2, Exception):
                    if not isinstance(val2, type(val1)):
                        diff.write(f"\n{idx} {f1} {arg1}\n")
                        diff.write(f"  {k1}: {type(val1)} {val1}\n")
                        traceback.print_exception(val1, file=diff)
                        diff.write(f"  {k2}: {type(val2)} {val2}\n")
                        traceback.print_exception(val2, file=diff)
                elif val1 != val2:
                    diff.write(
                        f"\n{idx} {f1} {arg1}\n"
                        f"  {k1}: {format_value(val1)}\n"
                        f"  {k2}: {format_value(val2)}\n"
                    )
        diff_text = diff.getvalue()
        if diff_text:
            self.fail(msg=diff_text)

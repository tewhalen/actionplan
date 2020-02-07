from collections.abc import MutableMapping
import itertools

"""
A wrapper around an existing dict that doesn't modify the underlying dict

... so you don't have to do an expensive copy if you just want to store changes.

"""


class WrappedDict(MutableMapping):
    """A dict-alike that (a) maintains an underlying dict object and (b) a dict on top
    that keeps track of changes and (c) is hashable."""

    def __init__(self, data=()):
        self.__wrapper = {}
        self.__underlying_dict = data
        self.frozen = False
        self._as_tuple = None
        self._frozen_dict = None
        # self.update(data)

    def wrapping(self):
        return self.__wrapper

    def inc(self, key, amount=1):
        if self.frozen:
            raise TypeError
        self[key] = self.get(key, 0) + amount

    def dec_to_zero(self, key, amount=1):
        if self.frozen:
            raise TypeError
        elif self.get(key, 0) > 0:
            self[key] = max(0, (self[key] - amount))

    def dec(self, key, amount=1):
        if self.frozen:
            raise TypeError
        self[key] = self.get(key, 0) - amount

    def __getitem__(self, key):
        if key in self.__wrapper:
            return self.__wrapper[key]
        else:
            return self.__underlying_dict[key]

    def __delitem__(self, key):
        if self.frozen:
            raise TypeError
        del self.__wrapper[key]

    def __setitem__(self, key, value):
        if self.frozen:
            raise TypeError
        self.__wrapper[key] = value

    def __iter__(self):
        if self.frozen:
            return iter(self._frozen_dict)
        return iter({**self.__wrapper, **self.__underlying_dict})

    def __len__(self):
        if self.frozen:
            return len(self._frozen_dict)
        return len(self.__wrapper) + len(self.__underlying_dict)

    def __repr__(self):
        if self.frozen:
            return f"{type(self).__name__}(F{self._frozen_dict})"
        return f"{type(self).__name__}({self.__wrapper}/{self.__underlying_dict})"

    def __hash__(self):
        # a little bit expensive, maybe
        return hash(self.as_tuple())

    def freeze(self):
        self.frozen = True
        self._frozen_dict = {
            **self.__underlying_dict,
            **self.__wrapper,
        }  # update underlying with wraper and save
        self._as_tuple = tuple(sorted(self.items()))

    def as_tuple(self):
        # we're cleverly using the "am i frozen" flag to store the result
        if not self.frozen:
            self.freeze()
        return self._as_tuple

    def child(self):
        if not self.frozen:
            self.freeze()
        return type(self)(self._frozen_dict)


if __name__ == "__main__":
    underlying_dict = {"a": 1, "b": 2, "c": 3}

    wd = WrappedDict(underlying_dict)
    assert wd == underlying_dict

    assert wd["a"] == 1

    wd["b"] = 9
    assert wd != underlying_dict

    assert wd["b"] == 9
    assert underlying_dict["b"] == 2
    wd["d"] = None
    assert wd != underlying_dict
    assert "d" not in underlying_dict

    seen_sets = {wd}

    wd_two = WrappedDict(underlying_dict)
    wd_two["b"] = 9
    wd_two["d"] = None

    assert wd_two in seen_sets
    wd_two["c"] = 1  # shoudl raise


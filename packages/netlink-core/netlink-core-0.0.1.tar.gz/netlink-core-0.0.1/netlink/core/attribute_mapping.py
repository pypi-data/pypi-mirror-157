import collections.abc


def _resolve_iterable(value):
    temp = []
    for i in value:
        if isinstance(i, (str, bytes)):
            temp.append(i)
            continue
        if isinstance(i, collections.abc.Mapping):
            temp.append(AttributeMapping(i))
            continue
        elif isinstance(i, collections.abc.Iterable):
            temp.append(_resolve_iterable(i))
            continue
        temp.append(i)
    return tuple(temp)


class AttributeMapping(collections.abc.Mapping):
    def __init__(self, d: collections.abc.Mapping):
        self._data = {k: v for k, v in d.items()}
        for i in self._data:
            if isinstance(self._data[i], (str, bytes)):
                continue
            if isinstance(self._data[i], collections.abc.Mapping):
                self._data[i] = AttributeMapping(self._data[i])
                continue
            if isinstance(self._data[i], collections.abc.Iterable):
                self._data[i] = _resolve_iterable(self._data[i])

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getattr__(self, item):
        if item in self._data:
            return self._data[item]
        raise AttributeError(item)

    def __repr__(self):
        return f'{str(self._data)}'


if __name__ == '__main__':
    a = dict(abc=dict(a=1, b='abc', c={1, 2, 3}, d=[1,2,3]))
    b = AttributeMapping(a)
    print(1)
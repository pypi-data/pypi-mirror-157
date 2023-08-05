import collections.abc
from ._item import Item


class List(collections.abc.Mapping):
    title = ''
    map = {}
    _data = {}
    _raw = {}

    def __init__(self, site, title: str = None):
        self._site = site
        self._list = site.get_list(title or self.title)
        self.rollback()

    def append(self, **kwargs):
        self._list.add_item(kwargs)

    add_item = append

    def rollback(self):
        self._data = {}
        self._raw = []
        for i in self._list.items.get().execute_query():
            self._raw.append(i)
            item = Item(self, i)
            self._data[item.id] = item

    def get_item_by_unique_id(self, id: int):
        return self._list.get_item_by_unique_id().execute_query()

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]

    @property
    def reverse_map(self):
        return {v: k for k, v in self.map.items()}

    def commit(self):
        for i in self._data.values():
            i.commit(lazy=True)
        self._list.context.execute_batch()

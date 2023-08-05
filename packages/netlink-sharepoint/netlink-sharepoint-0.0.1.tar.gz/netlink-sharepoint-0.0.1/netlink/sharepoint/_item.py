import collections.abc


class _NoneItem:
    id = None

    def get_property(self, name):
        return self.id


class Item(collections.abc.MutableMapping):
    _dirty = None
    _item = None

    def __init__(self, sharepoint_list, item=None):
        self._sharepoint_list = sharepoint_list
        self._data = {'id': None}
        self.rollback(item)

    def rollback(self, item=None):
        if item is None:
            if self._data['id'] is None:
                item = _NoneItem()
            else:
                item = self._sharepoint_list.get_item_by_unique_id(self._data['id'])
        else:
            self._data['id'] = item.id
        self._data = {py_name: item.get_property(sp_name)
                      for sp_name, py_name in self._sharepoint_list.map.items()}
        self._dirty = set()
        self._item = item

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        if key in self._data:
            self._data[key] = value
            self._dirty.add(key)
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        raise NotImplementedError

    def __getattr__(self, item):
        if item not in self._data:
            raise AttributeError(item)
        return self.get(item, None)

    def commit(self, lazy: bool = False):
        if self.id is None and self._dirty:
            self._item = self._sharepoint_list.add_item()
        for i in self._dirty:
            self._item.set_property(self._sharepoint_list.reverse_map[i], self._data[i]).update()
        self._dirty.clear()
        if not lazy:
            self._item.execute_query()

    def __str__(self):
        return f'{self._sharepoint_list.title}: {self._data}'

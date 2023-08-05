from typing import Dict, List, Union, TypeVar

K = TypeVar('K')
V = TypeVar('V')


def get(d: Union[Dict[K, V], Dict[K, Dict]], k: Union[List[K], K]) -> Union[None, V]:
    """
    Get the value of a key or nested keys in a dictionary, returning None if it doesn't exist.
    :param d: dictionary to look in
    :param k: key or list of keys
    :return: an item in the dictionary, or None
    """
    if not isinstance(k, list):
        return d.get(k)

    if len(k) == 0:
        return None

    res = d
    for key in k:
        if res is None:
            return None
        res = res.get(key)

    return res

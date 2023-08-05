import re
import xml.etree.ElementTree as ET
from typing import List

from netdot.exceptions import NetdotError


def filter_dict(dict, kword):
    """
    This function descends into the Multi-level
    dictionary and returns a list of [filtered] key value pairs

    Usage:
      dot.filter_dict(dict, ['list', 'of', '.*keywords'])

    Returns:
      Multi-level dictionary on success
    """
    data = {}
    for top_k, top_v in dict.items():
        data[top_k] = {}
        for mid_k, mid_v in top_v.items():
            data[top_k][mid_k] = {}
            for bot_k, bot_v in mid_v.items():
                if kword:
                    re_comb = "(" + ")|(".join(kword) + ")"
                    if re.match(re_comb, bot_k):
                        data[top_k][mid_k][bot_k] = bot_v
                    else:
                        data[top_k][mid_k][bot_k] = bot_v
    return data


def dump(object):
    for property, value in vars(object).iteritems():
        f'{property} : {value}'


def flatten(lst: List[List]) -> List:
    ret_list = []
    for inner_list in lst:
        ret_list.extend(inner_list)
    return ret_list


def sslice(lst: List, limit=None, offset=None) -> List:
    """Get a slice of a list.

    Args:
        lst (List): The list to slice.
        limit (int, optional): How many items to return from the list. Defaults to all items.
        offset (int, optional): Offset the limit, to enable paging behavior. Defaults to 0.

    Returns:
        List: The sliced chunk of the list.
    """
    if limit is None:
        limit = len(lst)
    if offset is None:
        offset = 0
    return lst[offset:offset+limit]

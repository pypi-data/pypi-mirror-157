import re
from typing import List



def flatten(lst: List[List]) -> List:
    ret_list = []
    for inner_list in lst:
        ret_list.extend(inner_list)
    return ret_list

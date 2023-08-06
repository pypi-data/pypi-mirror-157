import random

from typing import Union, Dict, List, Any


def new_id():
    id_str = ''
    for i in range(16):
        b = random.randint(0, 255)
        id_str += f'{b:02x}'
    return id_str


JSONVal = Union[str, int, float, bool, Dict[str, any], List[Any]]

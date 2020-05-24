from PyQt5.QtCore import QSize


def one(iterable):
    as_list = list(iterable)
    length = len(as_list)
    if length == 0:
        raise IndexError("Expected one element but found none")
    elif length == 1:
        return as_list[0]
    else:
        raise ValueError(f"Expected one element but found {length}")


def is_none_or_empty(val):
    if val is None or val == "":
        return True
    return False


def to_qsize(val: str) -> QSize:
    (x, y) = val.split(",")
    return QSize(int(x), int(y))

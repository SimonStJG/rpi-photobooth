def one(iterable):
    as_list = list(iterable)
    length = len(as_list)
    if length == 0:
        raise IndexError("Expected one element but found none")
    elif length == 1:
        return as_list[0]
    else:
        raise ValueError(f"Expected one element but found {length}")

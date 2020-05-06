def depth(obj):
    """Get object depth"""
    if isinstance(obj, dict):
        return max([1 + depth(v) for v in obj.values()] or [0])
    if isinstance(obj, (list, tuple, set)):
        return max([depth(v) for v in obj] or [0])
    return 0


def length(obj):
    """Get object length"""
    if isinstance(obj, dict):
        return sum([length(v) for v in obj.values()] or [0])
    if isinstance(obj, (list, tuple, set)):
        return max([length(v) for v in obj] or [0]) * len(obj)
    return 1


def _transform(dict_array):
    pass


def to_xlsx(dict_array):
    pass

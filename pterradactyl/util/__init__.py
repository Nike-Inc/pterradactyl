import itertools


def merge_dict(*args):
    return dict(
        list(
            itertools.chain.from_iterable(
                [list(arg.items()) for arg in args]
            )
        )
    )


def lookup(data, *args, default=None):
    for arg in args:
        if arg in data.keys():
            return data[arg]

    return default


def as_list(*args):
    return list(itertools.chain.from_iterable([arg if type(arg) is list else [arg] for arg in args]))


def memoize(func):
    memo = {}

    def inner(*args, **kwargs):
        key = str(dict(args=args, kwargs=kwargs))
        if key not in memo:
            memo[key] = func(*args, **kwargs)
        return memo[key]

    return inner

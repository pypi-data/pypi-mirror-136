"""pyhof: Python High Order Functions library"""
from functools import reduce, wraps
from itertools import accumulate
from inspect import getargspec

__version__ = "0.1.3"

__all__ = [
    "compose",
    "composer",
    "const",
    "constantly",
    "curry",
    "curryr",
    "flip",
    "foldl",
    "foldl1",
    "foldr",
    "foldr1",
    "identity",
    "outer_product",
    "scanl",
    "scanl1",
    "scanr",
    "scanr1",
    "power",
]


def _prepend(value, iterable):
    yield value
    for element in iterable:
        yield element


def partial(func, *args, **kwargs):
    """partial: Partially applies arguments.
    New keyworded arguments extend and override kwargs."""
    return lambda *a, **kw: func(*(args + a), **dict(kwargs, **kw))


def partialr(func, *args, **kwargs):
    """partialr: Partially applies last arguments.
    New keyworded arguments extend and override kwargs."""
    return lambda *a, **kw: func(*(a + args), **dict(kwargs, **kw))


def curry(func, n=None):
    """curry: make function into a curried version"""
    if n is None:
        n = len(getargspec(func).args)

    if n <= 1:
        return func
    elif n == 2:
        return lambda x: lambda y: func(x, y)
    else:
        return lambda x: curry(partial(func, x), n - 1)


def curryr(func, n=None):
    """curryr: make function into a curried version, using last argument"""
    if n is None:
        n = len(getargspec(func).args)

    if n <= 1:
        return func
    elif n == 2:
        return lambda x: lambda y: func(y, x)
    else:
        return lambda x: curryr(partialr(func, x), n - 1)


def flip(func):
    """flip: returns a function with reversed position arguments of func"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*reversed(args), **kwargs)

    return wrapper


def identity(x):
    """identity: return the argument"""
    return x


def compose(*funcs):
    """compose: compose the funcs into a single function"""
    if len(funcs) == 0:
        return identity
    elif len(funcs) == 1:
        return funcs[0]
    else:
        return lambda *args, **kwargs: compose(*(funcs[:-1]))(
            funcs[-1](*args, **kwargs)
        )


def composer(*funcs, **kwargs):
    """compose: reverse compose the funcs into a single function"""
    return compose(*reversed(funcs))


def const(x, *args, **kwargs):
    """const: returns x ignoring other arguments"""
    return x


def constantly(x):
    """constantly: returns the function const(x)"""

    @wraps(const)
    def wrapper(*args, **kwargs):
        return x

    return wrapper


def foldl(func, start, iterable):
    """foldl: foldl is folding a function from left to right

    func: the function to reduce with
    start: the initial starting value
    iterable: the iterable to reduce over
    """
    return reduce(func, iterable, start)


def foldl1(func, iterable):
    """foldl1: foldl1 is folding a function from left to right without an initial value

    func: the function to reduce with
    iterable: the iterable to reduce over
    """
    return reduce(func, iterable)


def _foldr(func, start, iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return start
    return func(first, _foldr(func, start, iterable))


def foldr(func, start, iterable):
    """foldr: foldr is folding a function from right to left

    func: the function to reduce with
    start: the initial starting value
    iterable: the iterable to reduce over
    """
    return _foldr(func, start, iter(iterable))


def _foldr1(func, iterable):
    first = next(iterable)
    try:
        return func(first, _foldr1(func, iterable))
    except StopIteration:
        return first


def foldr1(func, iterable):
    """foldr1: foldr1 is folding a function from right to left without an initial value

    func: the function to reduce with
    iterable: the iterable to reduce over
    """
    try:
        return _foldr1(func, iter(iterable))
    except StopIteration:
        raise TypeError("foldr1() of empty sequence")


def scanl(func, start, iterable):
    """scanl: similar to foldl but also outputs intermediate values

    func: the function to scan with
    start: the initial starting value
    iterable: the iterable to scan over"""
    return list(accumulate(_prepend(start, iterable), func))


def scanl1(func, iterable):
    """scanl: similar to foldl1 but also outputs intermediate values

    func: the function to scan with
    iterable: the iterable to scan over"""
    return list(accumulate(iterable, func))


def _scanr(func, start, iterable):
    try:
        first = next(iterable)
    except StopIteration:
        yield start
        raise StopIteration
    rest = _scanr(func, start, iterable)
    value = next(rest)
    yield func(first, value)
    yield value
    for value in rest:
        yield value


def scanr(func, start, iterable):
    """scanr: similar to foldr but also outputs intermediate values

    func: the function to scan with
    start: the initial starting value
    iterable: the iterable to scan over"""
    return list(_scanr(func, start, iter(iterable)))


def _scanr1(func, iterable):
    first = next(iterable)
    try:
        rest = _scanr1(func, iterable)
        value = next(rest)
        yield func(first, value)
        yield value
        for value in rest:
            yield value
    except StopIteration:
        yield first


def scanr1(func, iterable):
    """scanr1: similar to foldr1 but also outputs intermediate values

    func: the function to scan with
    iterable: the iterable to scan over"""
    return list(_scanr1(func, iter(iterable)))


def power(func, n):
    """power: return a function that applies func n times"""
    return compose(*([func] * n))


def outer_product(func, x, y):
    """outer_product: outer product of func with x and y"""
    res = []
    tmp = []
    for i in x:
        tmp = []
        for j in y:
            tmp.append(func(i, j))
        res.append(tmp)
    return res

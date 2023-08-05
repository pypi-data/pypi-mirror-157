from jft.string.format import f as format_one
f = lambda _l, fn=format_one: [fn(π) for π in _l]
t = lambda: list('abc') == f(list('abc'), lambda x: x)
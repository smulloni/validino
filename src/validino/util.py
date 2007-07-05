try:
    from functools import partial
except ImportError:
    def partial(func, *args, **kw):
        def inner(*_args, **_kw):
            d = kw.copy()
            d.update(_kw)
            return func(*(args + _args), **d)
        return inner


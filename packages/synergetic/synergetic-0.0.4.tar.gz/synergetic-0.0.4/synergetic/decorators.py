import functools


def add_defaults(defaults: dict):  # func should be init method
    def decorator_add_defaults(func):
        @functools.wraps(func)
        def wrapper_add_defaults(**kwargs):
            for key in defaults:
                if kwargs[key] is None:

        return wrapper_add_defaults
    return decorator_add_defaults



d = dict()
def decorator(func):
    def wrapper(**kwargs):
        for key in

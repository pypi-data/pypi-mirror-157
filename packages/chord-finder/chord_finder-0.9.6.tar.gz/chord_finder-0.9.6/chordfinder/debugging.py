# Borrowed from https://stackoverflow.com/questions/6200270/decorator-that-prints-function-call-details-parameters-names-and-effective-valu

import inspect, logging


def dump_args(func):
    """ Decorator to print function call details.
    This includes parameters names and effective values. """
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]}={0[1]!r}".format, func_args.items()))
        logging.debug(f"{func.__module__}.{func.__qualname__} ( {func_args_str} )")
        return func(*args, **kwargs)
    return wrapper

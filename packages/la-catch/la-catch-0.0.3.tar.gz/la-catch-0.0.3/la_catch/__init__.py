from typing import Callable, Any
from xmlrpc.client import Boolean


def catch(
    exceptions: Exception | tuple = Exception,
    call: Callable = lambda *args, **kwargs: None,
    ret: Any = ...,
    include_args: bool = True,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as exception:
                if include_args:
                    call_return = call(*args, exception, **kwargs)
                else:
                    call_return = call(exception)

                if ret is not Ellipsis:
                    return ret

                return call_return

        return wrapper

    return decorator

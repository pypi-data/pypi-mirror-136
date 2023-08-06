from typing import Callable, Any


def catch(
    exceptions: Exception | tuple = Exception,
    call: Callable = lambda *args, **kwargs: None,
    ret: Any = ...,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as exception:
                call_return = call(*args, exception, **kwargs)

                if ret is not Ellipsis:
                    return ret

                return call_return

        return wrapper

    return decorator

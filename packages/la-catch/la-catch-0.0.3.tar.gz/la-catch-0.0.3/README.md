# la-catch
Decorator to catch exception(s) and call function to handle the error. Can also define a return value to the function after catching.  

# install
`pip install la-catch`  

# syntax
```python
@catch(exceptions, call, ret)
```
`exceptions` - Exception or Tuple of exceptions to be captured  
`call` - function to be called in case of exceptions being raised  
`ret` - value to be returned by the main function in case of exceptions being raised  

`call` receives the same arguments from the decorated function but it appends the exception raised to the list of arguments (`*args`).  
In case an exception is raised and no `ret` was defined, the return will be the same that `call` would return.  

# usages
Let's say that you just expect a function to try running something and if fails ignore and continue the program logic. In this case you just want to catch and ignore the exception:  
```python
from la_catch import catch


@catch(Exception)
def example():
    raise Exception("What a great day to raise an exception")
```

Most of times you want at least to print the exception, in this case you can pass a function to be called. This function will receive the exception as the last argument for you use as you like.  
```python
from la_catch import catch


def func(e):
    print("Look what i catched mommy:", e)


@catch(Exception, func)
def example():
    raise Exception("You will never catch me alive")
```

If all that you want is print the exception/traceback, i would recommend you passing `logging.exception` as `call`.  
```python
import logging
from la_catch import catch


@catch(Exception, logging.exception)
def example():
    raise Exception("I love to read tracebacks")
```

Let's say that you know how to deal with the raised problem, now you want the function to return the solution of the problem. You can make `call` return the expected resolution.  
```python
from la_catch import catch


def func(e):
    if isinstance(e, ZeroDivisionError):
        print("You can't divide by zero you dummy")
        return 0
    return 1


@catch(Exception, func)
def example():
    return 0/0
```

Okay okay, but now you want to log the exception and return something so you program doesn't crash. Better than creating a function just for this two things is passing to `ret` the value to return in case of this exception.  
```python
import logging
from la_catch import catch


@catch(Exception, logging.exception, 0)
def example():
    return 0/0
```

Of course that i am using `Exception` everywhere but you could use other exception or multiple exceptions!  
```python
from la_catch import catch


@catch((ZeroDivisionError, OverflowError, FloatingPointError), logging.exception, 0)
def example():
    return 0/0
```

If you want to make different things to different exceptions just decorate with one more catch.  
```python
import logging
from la_catch import catch


@catch(OverflowError, logging.exception, None)
@catch(ZeroDivisionError, logging.exception, 0)
def example():
    return 0/0
```

Just remember that exception is always pass as the last argument from `call` (not counting **kwargs).  
```python
from la_catch import catch


def func(a, b, e):
    print("I have zero tolerance for this error... got it?")


@catch(ZeroDivisionError, func, 0)
def example(a, b):
    return a/b
```

The default behaviour is including the function arguments in your `call`, but you can choose not to send them. For example, you don't need this extra arguments in the `logging.exception`.  
```python
import logging
from la_catch import catch


@catch(Exception, logging.exception, include_args=False)
def example(a, b, c, d=1, e=2, f=3):
    raise Exception("You are a picky eater")
```

__all__ = [
    "Err",
    "formatter",
    "prompt",
    "option",
    "yesno",
    "confirm"
]

from collections import namedtuple
import inspect
import typing

import undefined


class Err:
    def __init__(self, message: str):
        self.message = message
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.message!r})"

Response = namedtuple("Response", ["kind", "value"], defaults = [None])

def formatter(response: tuple[str, typing.Any]) -> None:
    kind, value = response
    
    if kind == "description":
        print(f"[+] {value}")
    
    elif kind == "default":
        print(f"[_] {value}")
    
    elif kind in ("conversion_failed", "unexpected_response", "processing_failed"):
        print(f"[!] {value}")
    
    elif kind == "option":
        idx, val = value
        print(f"[{idx}] {val}")
    
    elif kind == "yesno":
        print("[y/n]")

def manage_input(
    func: typing.Callable[[typing.Any], typing.Any],
    default = undefined,
    convert = str,
    expect = lambda x: True,
    fallback = lambda exc: None,
    ps = "> "
):
    """
    Parameters
    ----------
    func
    
    default
        A default value that will be used in
        case the user only hits newline. When
        nothing is provided as default the
        response will be an empty string.
    
    convert
        A callable that takes one argument and
        returns the converted value.
    
    expect
        A callable that takes one argument as the
        converted value and decides whether to
        pass or not.
    
    fallback
        A callable taking an exception as the
        single argument and performing actions
        when the user hits Ctrl + C or EOF.
        This callable should either return an
        alternative value or quit the program.
    
    ps
        A prompt string.
    
    Returns
    ------
    The function's return value if not `Err`
    """
    # check if function takes exactly one
    # positional argument
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    if (len(params) != 1) or (params[0].kind != inspect.Parameter.POSITIONAL_OR_KEYWORD):
        raise ValueError(f"{func!r} requieres exactly one positional argument")
    
    doc = inspect.cleandoc(func.__doc__ or "")
    yield Response("description", doc)
    #print(f"[+] {doc}")
    
    if default is not undefined:
        yield Response("default", default)
        #print(f"[_] {default}")
    
    while True:
        try:
            response = input(ps)
        
        except (KeyboardInterrupt, EOFError) as exc:
            response = fallback(exc)
        
        else:
            yield Response("input", response)
            
            # assign default if needed
            # does not apply for fallback return value
            if not response and default is not undefined:
                response = default
        
        # convert response
        try:
            response = convert(response)
        
        except Exception as exc:
            yield Response("conversion_failed", exc)
            #print(f"[!] {exc}")
            continue
        
        # pass response to expect
        if not expect(response):
            yield Response("unexpected_response", "unexpected response")
            #print("[!] unexpected response")
            continue
        
        # pass response to function
        result = func(response)
        if isinstance(result, Err):
            yield Response("processing_failed", result.message)
            #print(f"[!] {result.message}")
            continue
        
        yield Response("return_value", result)
        break
        #return result

def prompt(**kwargs: typing.Any):
    """
    Decorator for a basic prompt
    """
    def decorator(func):
        def wrapper():
            extra = {}
            
            # function annotations will act as
            # converters
            annots = func.__annotations__
            if annots:
                # the function should only
                # have exactly one argument
                convert = list(annots.values())[0]
                extra["convert"] = convert
            
            for response in manage_input(
                func,
                **(kwargs | extra)
            ):
                formatter(response)
            return response.value
        return wrapper
    return decorator

def option(*options, **kwargs: typing.Any):
    """
    Decorator for a prompt with a list of options.
    
    Paramters
    ---------
    options
        Strings 
    """
    def decorator(func):
        def wrapper():
            for response in manage_input(
                func,
                convert = int,
                expect = lambda x: x in range(1, len(options) + 1),
                **kwargs
            ):
                formatter(response)
                if response.kind == "description":
                    for option in enumerate(options, start = 1):
                        formatter(Response("option", option))
            return response.value
        return wrapper
    return decorator

def yesno(
    truthcheck: typing.Callable[[str], bool] = lambda x: True if x.strip().upper() in ("Y", "YES") else (False if x.strip().upper() in ("N", "NO") else None),
    **kwargs: typing.Any
):
    """
    Decorator for a prompt that expects a
    truth value (yes or no)
    
    Parameters
    ----------
    truthcheck
        Callable interpreting the input as `True`,
        `False` or `None` (invalid input).
    """
    def decorator(func):
        def wrapper():
            for response in manage_input(
                func,
                convert = truthcheck,
                expect = lambda x: x is not None,
                **kwargs
            ):
                formatter(response)
                if response.kind == "description":
                    formatter(Response("yesno"))
            return response.value
        return wrapper
    return decorator

def confirm(**kwargs):
    """
    Decorator for a prompt that does not
    take any input. Because the function
    still requires one argument as input
    this serves as syntastic sugar. `None`
    will be passed as the response.
    """
    def decorator(func):
        def wrapper():
            for response in manage_input(
                func,
                **kwargs
            ):
                formatter(response)
            return None
        return wrapper
    return decorator

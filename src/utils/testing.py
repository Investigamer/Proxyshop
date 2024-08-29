"""
* Utils: Testing
"""
# Standard Library Imports
from time import perf_counter
from operator import itemgetter
from typing import Optional, Union, Callable, Any

# Third Party
import colorama
from colorama import Fore

"""
* Util Decorators
"""


def time_function(func: Callable) -> Callable:
    """Print the execution time in seconds of any decorated function.

    Args:
        func: The wrapped function.
    """
    def wrapper(*args, **kwargs):
        """Wraps the function call in a `perf_counter` timer."""
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        execution_time = end_time - start_time
        print(f"Executed {func.__name__} in {execution_time:.4f} seconds")
        return result
    return wrapper


"""
* Util Funcs
"""


def test_execution_time(
    funcs: list[tuple[Callable, list[Any]]],
    iterations: int = 1000,
    reset_func: Optional[Callable] = None
) -> None:
    """Test the execution time of a new function against an older function.

    Args:
        funcs: List of tuples containing a func to test and args to pass to it.
        iterations: Number of calls to each function to perform.
        reset_func: Optional function to call to reset app state between actions.
    """
    # Track results
    res: dict[str, Union[None, int, float, str, list]] = {
        'value': None, 'average': 0, 'times': [], 'name': ''}

    # Test configuration
    colorama.init(autoreset=True)
    results: list[dict[str, Union[None, int, float, str, list]]] = []

    # Test each function
    for func, args in funcs:
        r = res.copy()
        for i in range(iterations):
            s = perf_counter()
            r['value'] = func(*args)
            r['times'].append(perf_counter()-s)
            if reset_func:
                reset_func()
        r['average'] = sum(r['times'])/len(r['times'])
        r['name'] = func.__name__
        results.append(r.copy())

    # Report results
    results, compare = sorted(results, key=itemgetter('average')), 0
    for i, r in enumerate(results):
        if i == 0:
            compare = r['average']
            print(f"{Fore.GREEN}{r['name']}: {r['average']}")
            continue
        delta = r['average'] - compare
        percent = round(delta / ((r['average'] + compare) / 2) * 100, 2)
        print(f"{r['name']}: {r['average']} ({percent}% Slower)")

    # Check if all values were the same
    check, values = f'{Fore.GREEN}SUCCESS', []
    for i, r in enumerate(results):
        if i == 0:
            values.append(r['value'])
            continue
        if r['value'] not in values:
            check = f'{Fore.RED}FAILED'
            break
    print(f"Values check: {check}")

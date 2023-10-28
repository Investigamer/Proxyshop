"""
TESTING UTILITIES
"""
# Standard Library
import time
from time import perf_counter
from operator import itemgetter
from typing import Optional, Union, Callable

# Third Party
import colorama
from colorama import Fore


"""
DECORATORS
"""


def time_function(func):
    """Print the execution time in seconds of any decorated function."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Executed {func.__name__} in {execution_time:.4f} seconds")
        return result
    return wrapper


"""
UTIL FUNCS
"""


def test_execution_time(
    new_func: Callable,
    old_func: Callable,
    iterations=1000,
    args=None,
    args_old=None,
    check_result=True,
    reset_func: Optional[Callable] = None
) -> None:
    """
    Test the execution time of a new function against an older function.
    @param new_func: New callable function to test.
    @param old_func: Older callable function to compare against.
    @param iterations: How many times to run these functions, higher means better sample size.
    @param args: Args to pass to the newer function, and older function unless specified in args_old.
    @param args_old: Args to pass to the older function.
    @param check_result: Whether to check if results match.
    @param reset_func: Optional function to call to reset app state between actions.
    """
    # TODO: Needs some major refactoring
    # Test configuration
    args = args or []
    args_old = args_old or args
    colorama.init(autoreset=True)
    results: list[dict[str, Union[None, int, float, str, list]]] = [
        {
            'value': None,
            'average': 0,
            'times': [],
            'type': 'Newer'
        },
        {
            'value': None,
            'average': 0,
            'times': [],
            'type': 'Older'
        }
    ]

    # Test new functionality
    for i in range(iterations):
        s = perf_counter()
        results[0]['value'] = new_func(*args)
        results[0]['times'].append(perf_counter()-s)
        if reset_func:
            reset_func()
    results[0]['average'] = sum(results[0]['times'])/len(results[0]['times'])

    # Test old functionality
    for i in range(iterations):
        s = perf_counter()
        results[1]['value'] = old_func(*args_old)
        results[1]['times'].append(perf_counter()-s)
        if reset_func:
            reset_func()
    results[1]['average'] = sum(results[1]['times'])/len(results[1]['times'])

    # Report results
    for i, res in enumerate(results):
        print(f"{res['type']} method: {res['average']}")

    # Compare results
    final = sorted(results, key=itemgetter('average'))
    slower = final[1]['average']
    faster = final[0]['average']
    delta = slower - faster
    percent = round(delta/((slower + faster)/2) * 100, 2)
    print(f"{Fore.GREEN}The {final[0]['type']} method is {percent}% faster!")
    if check_result:
        print(f"Results check: {Fore.GREEN+'SUCCESS' if final[0]['value'] == final[1]['value'] else Fore.RED+'FAILED'}")
        if final[0]['value']:
            print(final[0]['value'])
            print(final[1]['value'])

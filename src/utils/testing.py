"""
TESTING UTILITIES
"""
import time


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

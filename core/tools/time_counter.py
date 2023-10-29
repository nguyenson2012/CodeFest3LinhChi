import time


def measure_time(func):
    """
    A decorator to measure the execution time of a function.
    Args:
        func (function): The function to measure the execution time of.
    Returns:
        function: The decorated function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time)
        print(f"Execution of {func.__name__} time: {execution_time:.6f} seconds")
        return result

    return wrapper

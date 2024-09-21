import logging
import subprocess
import time
from functools import wraps

from PyQt6.QtWidgets import QMessageBox

from natug import constants

logger = logging.getLogger(__name__)


def remove_duplicates(iterable):
    """
    Remove duplicates from an iterable.

    Args:
        iterable: The iterable to remove duplicates from.

    Returns:
        list: The iterable with duplicates removed.
    """
    output = []
    for item in iterable:
        if item not in output:
            output.append(item)
    return output


def rgb_to_hex(rgb):
    """
    Convert an rgb tuple to a hex code.

    Args:
        rgb: The rgb tuple to convert.

    Returns:
        str: The hex code.
    """
    # Make all the elements in the tuple integers
    return "#{:02x}{:02x}{:02x}".format(*[int(i) for i in rgb[:3]])


def hex_to_rgb(hex_code):
    """
    Convert a hex code to an rgb tuple.

    Args:
        hex_code: The hex code to convert.

    Returns:
        tuple: The rgb tuple.
    """
    return tuple(int(hex_code[i : i + 2], 16) for i in (1, 3, 5))


def show_in_file_explorer(filepath):
    """Open the filepath in the file explorer."""
    logger.info(f'Opening "%s" in file explorer.', filepath)
    subprocess.Popen(f'explorer /select, "%s"', filepath)


def bases_only(blended: str):
    """Take an input string and return a version with only bases."""
    new_bases = []
    for potential_base in blended:
        if potential_base.upper() in constants.bases.DNA or potential_base == " ":
            new_bases.append(potential_base.upper())
    return "".join(new_bases)


def singleton(orig_cls):
    """Decorator to convert a class instance into a singleton."""
    # https://igeorgiev.eu/python/design-patterns/python-singleton-pattern-decorator/

    orig_new = orig_cls.__new__
    instance = None

    @wraps(orig_cls.__new__)
    def __new__(cls, *args, **kwargs):
        nonlocal instance  # we are referring to the above instance variable
        if (
            instance is None
        ):  # if there is no instance of the class already than create one
            instance = orig_new(cls, *args, **kwargs)
        return instance  # return class instance

    orig_cls.__new__ = __new__
    return orig_cls


def factors(number):
    # https://www.programiz.com/python-programming/examples/factor-number
    output = []
    for i in range(1, number + 1):
        if number % i == 0:
            output.append(i)
    return output


def confirm(parent, title, msg):
    choice = QMessageBox.warning(
        parent,
        title,
        msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if choice == QMessageBox.StandardButton.Yes:
        return True
    else:
        return False


def warning(parent, title, msg):
    QMessageBox.critical(
        parent,
        title,
        msg,
        QMessageBox.StandardButton.Ok,
    )


def reverse_hidenness(potentially_hidden_item):
    """Reverse the hiddenness of a widget"""
    if potentially_hidden_item.isHidden():
        potentially_hidden_item.show()
    else:
        potentially_hidden_item.hide()


def inverse(integer: int) -> int:
    """
    Returns int(not bool(integer)).

    Args:
        integer: Either 0 or 1.

    Returns:
        int: 0 or 1.
    """
    return int(not bool(integer))


class Timer:
    """
    Context manager to time a task.
    """

    def __init__(self, task_name="", logger: logging.Logger = None, round_to=3):
        """
        Initialize the Timer.

        Args:
            task_name: The name of the task to log.
            logger: The logger to log the time to.
            round_to: The number of decimal places to round the time to.
        """
        self.logger = logger
        self.task_name = task_name
        self.round_to = round_to

    def __enter__(self):
        """
        Start the timer.
        """
        self.start = time.time()

    def __exit__(self, *args):
        """
        End the timer and log the time.
        """
        self.end = time.time()
        self.duration = self.end - self.start
        msg = f"{self.task_name} took {round(self.duration, self.round_to)}s."

        try:
            self.logger.info(msg)
        except AttributeError:
            print(msg)


def timer(logger: logging.Logger = None, task_name="", round_to=3):
    """
    Decorator to time a function.

    Args:
        func: The function to time.
        logger: The logger to log the time to.
        task_name: The name of the task to log.
        round_to: The number of decimal places to round the time to.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Timer(logger=logger, task_name=task_name, round_to=round_to):
                return func(*args, **kwargs)

        return wrapper

    return decorator

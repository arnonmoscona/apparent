#  Copyright (c) Arnon Moscona 2023. under Apache2 license
"""The main module for explicit timing measurement support. See @timed"""
import math
from contextlib import AbstractContextManager
from dataclasses import asdict, dataclass
from enum import Enum
from functools import wraps
from time import perf_counter
from typing import Protocol, TypeVar


class Units(Enum):
    MIN = 'min'
    SEC = 'sec'
    MSEC = 'msec'


_CONVERSION_FACTOR = {
    Units.MIN: 1.0 / 60.0,
    Units.SEC: 1.0,
    Units.MSEC: 1000
}


@dataclass
class TimerResults:
    """Results from a timer: basic descriptive statistics (default in seconds).
    This class is generally produced by timers and not instantiated directly by library users"""
    total_time: float
    count: int
    mean: float
    stdevp: float
    min: float
    max: float
    timer_name: str
    units: Units = Units.SEC

    def convert(self, units: Units) -> 'TimerResults':
        """Convert the timer results to the given units"""
        factor = _CONVERSION_FACTOR[units] if self.units == Units.SEC \
            else _CONVERSION_FACTOR[units] / _CONVERSION_FACTOR[self.units]
        return TimerResults(
            total_time=self.total_time * factor,
            count=self.count,
            mean=self.mean * factor,
            stdevp=self.stdevp * factor,
            min=self.min * factor,
            max=self.max * factor,
            timer_name=self.timer_name,
            units=units)

    def dict(self, verbose: bool = True) -> dict:
        """Convert the timer results to a dictionary representation."""
        return asdict(self) if verbose else {'timer_name': self.timer_name,
                                             'total_time': self.total_time,
                                             'count': self.count,
                                             'mean': self.mean,
                                             'units': self.units}

    def round(self, digits: int = 1) -> 'TimerResults':
        """Round the timer results to the given number of digits. Useful for presentation and for comparison."""
        return TimerResults(
            total_time=round(self.total_time, digits),
            count=self.count,
            mean=round(self.mean, digits),
            stdevp=round(self.stdevp, digits),
            min=round(self.min, digits),
            max=round(self.max, digits),
            timer_name=self.timer_name,
            units=self.units)


class RunningVariance:
    """Variance using the shifted data algorithm for unbiased sample variance as described in
    https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Computing_shifted_data"""
    def __init__(self):
        # All variable names are taken from the Wikipedia article to make it easier to follow
        self._k: float = 0  # This will be the first value from the sample (shift value)
        self._n: int = 0  # sample count
        self._ex: float = 0  # sum of differences from shift value
        self._ex2: float = 0  # sum of squared differences from shift value

    def add(self, x: float):
        """Add a value to the running variance"""
        if self._n == 0:
            self._k = x
        self._n += 1
        self._ex += x - self._k
        self._ex2 += (x - self._k) ** 2

    def mean(self) -> float:
        """Return the mean of the added values"""
        return self._k + self._ex / self._n

    def variance(self, population: bool = False) -> float:
        """Computes the variance of the added values. By default, uses sample variance. Can be population variance"""
        return (self._ex2 - self._ex ** 2 / self._n) / (self._n if population else self._n - 1)

    def stdev(self) -> float:
        """Computes the standard deviation of the added values.
        By default, uses sample variance. Can be population variance"""
        return math.sqrt(self.variance())

    def stdevp(self) -> float:
        """Computes the population standard deviation of the added values. """
        return math.sqrt(self.variance(population=True))

    @property
    def n(self):
        """Return the number of values added"""
        return self._n


class Timer(AbstractContextManager):
    """A context manager for timing operations. Usually used in conjunction with a timer registry.
    Most of the time you will find yourself using one of the associated function decorators, such as @timed"""
    def __init__(self, name=None):
        if not isinstance(name, str):
            raise TypeError('name must be a string')
        self.name = name
        self.variance: RunningVariance = RunningVariance()
        self.sum = 0
        self._min = math.inf
        self._max = -math.inf
        self.start_time = 0

    def __enter__(self):
        self.start_time = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = (perf_counter() - self.start_time)
        self.variance.add(elapsed)
        self.sum += elapsed
        self._min = min(self._min, elapsed)
        self._max = max(self._max, elapsed)

    @property
    def counter(self) -> int:
        """The number of times the timer has been invoked"""
        return self.variance.n

    @property
    def mean(self) -> float:
        """Mean of all observations. NaN if no observations have been recorded"""
        return self.variance.mean() if self.counter > 0 else math.nan

    @property
    def stdevp(self) -> float:
        """Population standard deviation of all observations. NaN if less than 2 observations have been recorded"""
        return self.variance.stdevp() if self.counter > 2 else math.nan

    @property
    def min(self) -> float:
        """Minimum of all observations. NaN if no observations have been recorded"""
        return self._min if self.counter > 0 else math.nan

    @property
    def max(self) -> float:
        """Maximum of all observations. NaN if no observations have been recorded"""
        return self._max if self.counter > 0 else math.nan

    def results(self, units=Units.SEC) -> TimerResults:
        """TimerResults object packaging the summary of current observations."""
        result = TimerResults(count=self.counter, total_time=self.sum,
                              mean=self.mean, stdevp=self.stdevp,
                              min=self.min, max=self.max,
                              timer_name=self.name)
        return result if units == Units.SEC else result.convert(units)


class TimerRegistry:
    """The default collection for all the timers. Used primarily with the @timed function decorator"""
    _shared: dict[str, Timer] = {}

    @classmethod
    def get(cls, name: str) -> Timer:
        """Returns a named registered timer, whether it already existed or not,
        allowing for easy reuse, e.g. in loops"""
        if name not in cls._shared:
            cls._shared[name] = Timer(name)
        return cls._shared[name]

    @classmethod
    def clear(cls):
        """Clears the entire registry. All timers gone."""
        cls._shared.clear()

    @classmethod
    def names(cls) -> list[str]:
        """Lists all the timer names in the registry.
        Since it is expected that the number of timers will be limited and the whole
        package is not intended for very high scale we return a concrete list rather than an iterator"""
        return list(cls._shared.keys())

    @classmethod
    def timers(cls) -> list[Timer]:
        """Lists all the timers in the registry.
        Since it is expected that the number of timers will be limited and the whole
        package is not intended for very high scale we return a concrete list rather than an iterator"""
        return list(cls._shared.values())

    @classmethod
    def reset(cls, name: str):
        """Resets / deletes a named timer."""
        if name in cls._shared:
            del cls._shared[name]


class TimerRegistryProtocol(Protocol):
    """For users who want to use some other implementation of a timer registry or want to
    use several timer registries for different contexts."""
    def get(self, name: str) -> Timer:
        ...

    def clear(self):
        ...

    def names(self) -> list[str]:
        ...

    def timers(self) -> list[Timer]:
        ...

    def reset(self, name: str):
        ...


TimerRegistryType = TypeVar('TimerRegistryType', TimerRegistryProtocol, TimerRegistry)
"""Any acceptable type for a timer registry."""


class Timed:
    """A simple class to associate a timer registry with the timed decorator. Rarely used."""
    _registry: TimerRegistryType = TimerRegistry

    @classmethod
    def registry(cls) -> TimerRegistryType:
        return cls._registry

    @classmethod
    def set_registry(cls, registry: TimerRegistryType):
        cls._registry = registry


def timed(f):
    """A decorator for timing a function.
    The decorated function will be called with a timer context manager to
    record the time spent in the decorated function.
    The timer registry that will be used for the decorated function is the one in effect
    at the time of the function declaration. The timer name is automatically determined
    from the module and qualified name of the function."""
    function_name = f'{f.__module__}.{f.__qualname__}()'

    @wraps(f)
    def wrapper(*args, **kwargs):
        timer = Timed.registry().get(function_name)
        with timer:
            return f(*args, **kwargs)

    return wrapper

# Apparent: a small library for observability

I created this library because in every job I've had I had to create some version of it, and I generally
Needed something simpler than some of the giant tools and frameworks, which I can use on my desktop
Without subscribing to some observability service.

This library is not intended to replace or compete with observability tools and dashboard, but is intended 
for day to day development use with a longer term objective of easy connectivity to observability 
Tools and frameworks. It is intended to remain small and compact.

## Installation

`python -m pip install apparent`

## Collect timing information

The most common use and the first to release as OSS is the timers functionality. There are many tools out there that do
Broadly similar things. In particular, two categories of tools are similar in some ways:

* Profilers (for example [yappi](https://github.com/sumerc/yappi))
* Micro-benchmarking tools of various kinds

This library is neither of the above. The idea here is to have lightweight, possibly permanent instrumentation for timing measurements of functions or sections of code of particular interest, which you may or may not expose to some 
monitoring facility, or simply expose during your debugging. The key drivers for this are:

* Very easy to add the instrumentation
* Does not require any additional dependencies, and optional ones are very small too
* Can produce reasonable reports easily, which should not require difficult interpretation
* Can collect timing data over a large number of samples with little space or time overhead
* Assumes deep familiarity of your own code base: as opposed to a profiler - where you may be working with someone else's
  code base and trying to discover some mystery bottleneck - the user of this library has more of an outside-in view
  where you have a pretty good idea upfront what you are interested in measuring (e.g. a specific computation, query, API endpoint).

Profilers are micro-benchmarking tools can be used commonly along with this for their own purposes.

### Examples

Measuring the timing of a function with the `@timed` decorator:

```python
from apparent.timing import timed

@timed
def f(x):
    ... 
```

Measuring the timing of a section of code with a registered timer.

```python
from apparent.timing import TimerRegistry

while some_consition_applies():
    do_something()
    with TimerRegistry.get('expensive_section'):
        do_expensive_section()
        ...
    ...
```

If you do not want to use a registered timer you can just use a `Timer` directly. But then you have to hold on to the instance  
to get any results out of it. For example:

```python
from apparent.timing import Timer

timer = Timer('timer1')
for i in range(5):
    with timer:
        ...

result = timer.results().round(4).dict()
```

#### Getting measurements from a timer

To get a measurement from a timer you need an instance of a `Timer` that has been used to collect the data. Then call the `results()` method on it. This returns a `TimerResults` instance summarizing the state of the timer at the time of the call. You can refer to the source code for detail, but a broad outline (may change over time - the source code is more authoritative than the partial copy below) is:

```python
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
        ...  # code removed for clarity

    def dict(self, verbose: bool = True) -> dict:
        """Convert the timer results to a dictionary representation."""
        ...  # code removed for clarity

    def round(self, digits: int = 1) -> 'TimerResults':
        """Round the timer results to the given number of digits. Useful for presentation and for comparison."""
        ...  # code removed for clarity
```

In most cases you will be using primarily the `@timed` decorator and occasionally `TimerRegistry.get(name)`. Both of these 
Result in named timers being registered in the timer registry and being retrievable by `TimerRegistry.get()`. Alternatively, all
Timer names can be retrieved by `TimerRegistry.names()` and all registered instances can be retrieved via `TimerRegistry.timers()`.  Using these you can produce a full listing of results of all timed code on demand.

The timer registry has some additional functionality, such as replacing the default instance with a custom registry, but those functionalities are beyond the scope of this document and will be discussed in a future document as the functionality matures.

##### Builtin reporting

**TBD**

## Counters and metrics (todo)

**TBD** *support for collecting ascending counters and metrics for exposing to observability frameworks.**



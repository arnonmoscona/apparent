#  Copyright (c) Arnon Moscona 2023. under Apache2 license
from unittest import TestCase
from unittest.mock import patch

from apparent.timing import Timed, Timer, TimerRegistry, Units, timed
from tests.common import CustomTimerRegistry


@patch('apparent.timing.perf_counter')
class TimerTests(TestCase):
    def setUp(self) -> None:
        TimerRegistry.clear()

    def test_timer(self, perf_counter):
        perf_counter.side_effect = [0.1, 0.2,
                                    0.3, 0.4,
                                    0.8, 1.0,
                                    1.2, 1.3,
                                    1.4, 1.8]

        timer = Timer('t')
        for i in range(5):
            with timer:
                ...

        result = timer.results().round(4).dict()
        expected = {
            'total_time': 0.9,
            'count': 5,
            'mean': 0.18,
            'stdevp': 0.1166,
            'min': 0.1,
            'max': 0.4,
            'timer_name': 't',
            'units': Units.SEC
        }
        result2 = timer.results(units=Units.MSEC).round(1).dict()
        expected2 = {
            'count': 5,
            'max': 400.0,
            'mean': 180.0,
            'min': 100.0,
            'stdevp': 116.6,
            'timer_name': 't',
            'total_time': 900.0,
            'units': Units.MSEC
        }
        self.assertEqual((expected, expected2), (result, result2))

    def test_timer_registry_base_case(self, perf_counter):
        perf_counter.side_effect = [0.1, 0.2]

        self.assertEqual(0, TimerRegistry.get('t1').counter)
        with TimerRegistry.get('t1'):
            ...

        self.assertEqual(1, TimerRegistry.get('t1').counter)

    def test_does_not_accept_non_strings(self, _):
        with self.assertRaises(TypeError):
            TimerRegistry.get(1)  # type: ignore

    def test_timer_registry_2_call_case(self, perf_counter):
        perf_counter.side_effect = [0.1, 0.2, 0.3, 0.4]

        with TimerRegistry.get('t2'):
            ...

        with TimerRegistry.get('t2'):
            ...

        self.assertEqual(2, TimerRegistry.get('t2').counter)

    def test_listing_timers(self, perf_counter):
        perf_counter.side_effect = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        with TimerRegistry.get('t1'):
            ...

        with TimerRegistry.get('t2'):
            ...

        with TimerRegistry.get('t2'):
            ...

        names = TimerRegistry.names()
        timers = TimerRegistry.timers()
        timer_names = [t.name for t in timers]
        counters = [t.counter for t in timers]

        expected = [['t1', 't2'], ['t1', 't2'], [1, 2]]
        actual = [names, timer_names, counters]
        self.assertEqual(expected, actual)

    def test_reset(self, perf_counter):
        perf_counter.side_effect = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        with TimerRegistry.get('t1'):
            ...

        with TimerRegistry.get('t2'):
            ...

        with TimerRegistry.get('t2'):
            ...

        TimerRegistry.reset('t2')

        names = TimerRegistry.names()
        timers = TimerRegistry.timers()
        timer_names = [t.name for t in timers]
        counters = [t.counter for t in timers]

        expected = [['t1'], ['t1'], [1]]
        actual = [names, timer_names, counters]
        self.assertEqual(expected, actual)

    def test_reset_non_existing_timer(self, _):
        TimerRegistry.reset('bogus')  # no KeyError
        self.assertEqual([], TimerRegistry.names())
        self.assertEqual([], TimerRegistry.timers())


class TimedMethodClassUnderTest:
    def __init__(self):
        self.counter = 0

    @timed
    def invoke(self):
        self.counter += 1


class TimedTests(TestCase):
    def setUp(self) -> None:
        Timed.set_registry(TimerRegistry)
        Timed.registry().clear()

    def test_timed_basic_use_case(self):

        @timed
        def f1():
            pass

        f1()
        f1()

        self.assertEqual(1, len(Timed.registry().timers()))
        self.assertEqual(['timer_tests.TimedTests.test_timed_basic_use_case.<locals>.f1()'], TimerRegistry.names())
        self.assertEqual(2, TimerRegistry.timers()[0].counter)

    def test_timed_with_method(self):
        sut = TimedMethodClassUnderTest()
        sut.invoke()
        sut.invoke()
        sut.invoke()
        self.assertEqual(['timer_tests.TimedMethodClassUnderTest.invoke()'], TimerRegistry.names())

    def test_timed_with_args(self):

        @timed
        def f2(a, b):
            return a, b

        c, d = f2(1, 2)

        self.assertEqual(['timer_tests.TimedTests.test_timed_with_args.<locals>.f2()'], TimerRegistry.names())
        self.assertEqual((1, 2), (c, d))

    def test_timed_with_kwargs(self):

        @timed
        def f3(a, num=None):
            return a, num

        c, d = f3(1, num=2)

        self.assertEqual(['timer_tests.TimedTests.test_timed_with_kwargs.<locals>.f3()'], TimerRegistry.names())
        self.assertEqual((1, 2), (c, d))

    def test_timed_with_custom_registry(self):
        @timed
        def f1():
            pass

        f1()

        registry = CustomTimerRegistry()
        Timed.set_registry(registry)

        @timed
        def f2():
            pass

        f2()

        self.assertEqual(['timer_tests.TimedTests.test_timed_with_custom_registry.<locals>.f1()'], TimerRegistry.names())
        self.assertEqual(['timer_tests.TimedTests.test_timed_with_custom_registry.<locals>.f2()'], registry.names())


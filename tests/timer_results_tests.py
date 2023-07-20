#  Copyright (c) Arnon Moscona 2023. under Apache2 license
from unittest import TestCase

from apparent.timing import TimerResults, Units


class TimerResultsTests(TestCase):
    def setUp(self) -> None:
        self.res1 = TimerResults(timer_name='res1',
                                 total_time=10,
                                 count=10,
                                 mean=1.1,
                                 min=0.5,
                                 max=1.6,
                                 stdevp=0.3456789)

    def test_init(self):
        expected = "TimerResults(total_time=10, count=10, mean=1.1, stdevp=0.3456789, min=0.5, max=1.6, " \
                   "timer_name='res1', units=<Units.SEC: 'sec'>)"
        self.assertEqual(expected, str(self.res1))

    def test_convert_to_msec(self):
        expected = TimerResults(total_time=10000,
                                count=10,
                                mean=1100.0,
                                stdevp=345.6789,
                                min=500.0,
                                max=1600.0,
                                timer_name='res1',
                                units=Units.MSEC)
        self.assertEqual(expected, self.res1.convert(Units.MSEC))

    def test_convert_to_sec(self):
        expected = TimerResults(total_time=10,
                                count=10,
                                mean=1.1,
                                stdevp=0.3456789,
                                min=0.5,
                                max=1.6,
                                timer_name='res1',
                                units=Units.SEC)
        self.assertEqual(expected, self.res1.convert(Units.SEC))

    def test_convert_to_min_rounded(self):
        expected = TimerResults(total_time=0.166667,
                                count=10,
                                mean=0.018333,
                                stdevp=0.005761,
                                min=0.008333,
                                max=0.026667,
                                timer_name='res1',
                                units=Units.MIN)
        self.assertEqual(expected, self.res1.convert(Units.MIN).round(6))

    def test_convert_to_min_rounded_default(self):
        expected = TimerResults(total_time=0.2,
                                count=10,
                                mean=0.0,
                                stdevp=0.0,
                                min=0.0,
                                max=0.0,
                                timer_name='res1',
                                units=Units.MIN)
        self.assertEqual(expected, self.res1.convert(Units.MIN).round())

    def test_dict(self):
        expected = {'count': 10,
                    'max': 1.6,
                    'mean': 1.1,
                    'min': 0.5,
                    'stdevp': 0.3456789,
                    'timer_name': 'res1',
                    'total_time': 10,
                    'units': Units.SEC}
        self.assertEqual(expected, self.res1.dict())

    def test_dict_verbose(self):
        expected = {'count': 10,
                    'max': 1.6,
                    'mean': 1.1,
                    'min': 0.5,
                    'stdevp': 0.3456789,
                    'timer_name': 'res1',
                    'total_time': 10,
                    'units': Units.SEC}
        self.assertEqual(expected, self.res1.dict(verbose=True))

    def test_dict_not_verbose(self):
        expected = {'count': 10,
                    'mean': 1.1,
                    'timer_name': 'res1',
                    'total_time': 10,
                    'units': Units.SEC}
        self.assertEqual(expected, self.res1.dict(verbose=False))

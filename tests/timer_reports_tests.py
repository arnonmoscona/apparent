#  Copyright (c) Arnon Moscona 2023. under Apache2 license
from time import sleep
from unittest import TestCase

from apparent.reports import ALL_TIMER_FIELDS, timer_summary_table
from apparent.timing import TimerRegistry, Units, timed
from tests.common import CustomTimerRegistry


@timed
def slow():
    sleep(0.05)


@timed
def slower():
    sleep(0.1)


@timed
def fast():
    pass


class TimerSummaryTableTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TimerRegistry.clear()
        fast()
        slow()
        slower()
        slower()
        slow()
        fast()
        fast()

    # FIXME test that the all fields matches the class definition

    def test_default_results(self):
        expected = [['timer_name', 'mean', 'count', 'max'],
                    ['timer_reports_tests.slower()', '102.325', '2', '103.764'],
                    ['timer_reports_tests.slow()', '53.787', '2', '53.787'],
                    ['timer_reports_tests.fast()', '0.002', '3', '0.004']]
        result = timer_summary_table()
        self.assertEqual(expected[0], result[0])
        self.assertEqual([r[2] for r in expected], [r[2] for r in result])

    def test_rounded_results(self):
        expected = [['timer_name', 'mean', 'count', 'max', 'min', 'stdevp'],
                    ['timer_reports_tests.slower()', '0.1', '2', '0.1', '0.1', 'nan'],
                    ['timer_reports_tests.slow()', '0.1', '2', '0.1', '0.1', 'nan'],
                    ['timer_reports_tests.fast()', '0.0', '3', '0.0', '0.0', '0.0']]
        result = timer_summary_table(units=Units.SEC, digits=1, fields=ALL_TIMER_FIELDS)
        # The rounding is so strong that this test should pass even though the actual sleep time varies a lot
        self.assertEqual(expected, result)

    def test_sort_on_name(self):
        expected = [['timer_name', 'count'],
                    ['timer_reports_tests.fast()', '3'],
                    ['timer_reports_tests.slow()', '2'],
                    ['timer_reports_tests.slower()', '2']]
        result = timer_summary_table(units=Units.SEC, digits=1, fields=('timer_name', 'count'),
                                     sort_field='timer_name')
        # The rounding is so strong that this test should pass even though the actual sleep time varies a lot
        self.assertEqual(expected, result)

    def test_invalid_sort_field(self):
        with self.assertRaises(ValueError):
            timer_summary_table(sort_field='bogus')

    def test_invalid_field(self):
        with self.assertRaises(ValueError):
            timer_summary_table(fields=('bogus', 'count'))

    def test_non_default_registry(self):
        expected = [['timer_name', 'mean', 'count', 'max']]
        result = timer_summary_table(registry=CustomTimerRegistry())
        self.assertEqual(expected, result)


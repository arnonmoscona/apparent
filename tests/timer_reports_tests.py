#  Copyright (c) Arnon Moscona 2023. under Apache2 license
from time import sleep
from unittest import TestCase

from apparent.reports import ALL_TIMER_FIELDS, DEFAULT_TIMER_FIELDS, timer_summary_table
from apparent.timing import TimerRegistry, TimerResults, Units, timed
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

    def test_constants(self):
        # noinspection PyUnresolvedReferences
        all_fields = set(TimerResults.__dataclass_fields__.keys())
        bad_fields = set(ALL_TIMER_FIELDS) - all_fields
        self.assertEqual(set(), bad_fields)
        bad_subset = set(DEFAULT_TIMER_FIELDS) - set(ALL_TIMER_FIELDS)
        self.assertEqual(set(), bad_subset)
        missing_fields = all_fields - set(ALL_TIMER_FIELDS)
        self.assertEqual(set(), missing_fields)

    def test_default_results(self):
        expected = [['timer_name', 'mean', 'count', 'max', 'total_time'],
                    ['timer_reports_tests.slower()', '103.912', '2', '104.984', '207.824'],
                    ['timer_reports_tests.slow()', '52.283', '2', '54.29', '104.566'],
                    ['timer_reports_tests.fast()', '0.005', '3', '0.009', '0.015']]
        result = timer_summary_table()
        self.assertEqual(expected[0], result[0])
        self.assertEqual([r[2] for r in expected], [r[2] for r in result])

    def test_rounded_results(self):
        expected = [['timer_name', 'mean', 'count', 'max', 'min', 'total_time', 'stdevp', 'units'],
                    ['timer_reports_tests.slower()', '0.1', '2', '0.1', '0.1', '0.2', 'nan', 'Units.SEC'],
                    ['timer_reports_tests.slow()', '0.1', '2', '0.1', '0.1', '0.1', 'nan', 'Units.SEC'],
                    ['timer_reports_tests.fast()', '0.0', '3', '0.0', '0.0', '0.0', '0.0', 'Units.SEC']]
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
        expected = [['timer_name', 'mean', 'count', 'max', 'total_time']]
        result = timer_summary_table(registry=CustomTimerRegistry())
        self.assertEqual(expected, result)

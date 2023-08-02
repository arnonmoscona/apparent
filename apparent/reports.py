#  Copyright (c) Arnon Moscona 2023. under Apache2 license

"""Reporting functionality for collected results"""
from typing import Iterable, List, Optional

from apparent.timing import TimerRegistry, TimerRegistryType, Units

ALL_TIMER_FIELDS = ('timer_name', 'mean', 'count', 'max', 'min', 'total_time', 'stdevp', 'units')
DEFAULT_TIMER_FIELDS = ('timer_name', 'mean', 'count', 'max', 'total_time')
DEFAULT_TIMER_SORT_FIELD = 'mean'


def timer_summary_table(fields: Iterable[str] = DEFAULT_TIMER_FIELDS,
                        sort_field: str = DEFAULT_TIMER_SORT_FIELD,
                        units: Units = Units.MSEC,
                        digits: int = 3,
                        registry: Optional[TimerRegistryType] = None) -> List[List[str]]:
    """
    Produces a CSV-like table of timer results. Highly recommended to use tabulate for presentation.
    Args:
        fields: the fields of TimerResults to include
        sort_field: the field to sort the results by. Time and count fields are sorted descending.
        units: The unites to use on all results. Default is Units.MSEC
        digits: The number of digits to round results to (the report is for human consumption)
        registry: the timer registry to use. Rarely used parameter.

    Returns:
        A CSV-like report: list of lists, all strings. You can get it nicely formatted with the tabulate package.
        Example `print(tabulate(report, headers='firstrow', tablefmt='rounded_outline'))`
    """
    registry = registry or TimerRegistry
    fields = fields or DEFAULT_TIMER_FIELDS

    # validate inputs
    bad_fields = [f for f in fields if f not in ALL_TIMER_FIELDS]
    if bad_fields:
        raise ValueError(f'invalid field(s) {bad_fields}')
    if sort_field not in ALL_TIMER_FIELDS:
        raise ValueError(f'invalid sort field {sort_field}')
    if digits < 0:
        digits = 0

    # collect all results
    results = [timer.results().convert(units) for timer in registry.timers()]

    # sort (sort order depends on field)
    reverse = sort_field in {'mean', 'min', 'max', 'count'}
    results.sort(key=lambda r: getattr(r, sort_field), reverse=reverse)
    results = [r.round(digits) for r in results]

    return [list(fields)] + [[str(getattr(r, f)) for f in fields] for r in results]

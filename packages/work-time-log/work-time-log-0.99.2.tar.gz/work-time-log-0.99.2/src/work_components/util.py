#!/usr/bin/env python3

""" Utils for the work module. """

import datetime as dt
import re
from collections import Counter
from typing import Dict, List, Optional


def remove_prefix(original: str, prefix: str) -> str:
    """Temporary replacement of removeprefix for Python versions < 3.9"""
    if original.startswith(prefix):
        return original[len(prefix) :]
    return original


def remove_suffix(original: str, suffix: str) -> str:
    """Temporary replacement of removeprefix for Python versions < 3.9"""
    if original.endswith(suffix) and len(suffix) > 0:
        return original[: -len(suffix)]
    return original


def verify_date_arguments(
    year: Optional[int], month: Optional[int] = None, day: Optional[int] = None
):
    """Ensure only the allowed combinations are set and all values are valid."""

    if year is None and month is None and day is None:
        return

    if year is None or (month is None and day is not None):
        raise ValueError("Invalid combination of year, month and day")

    month = month or 1
    day = day or 1
    # datetime verifies the validity of the given date
    dt.datetime(year, month, day)


def minutes_difference(start: dt.datetime, end: dt.datetime) -> float:
    """Calculates the minutes between start and end time. If end < start, the result is
    negative!"""
    return (end - start) / dt.timedelta(minutes=1)


def get_period(period_start: dt.date, period_end: dt.date) -> List[dt.date]:
    """
    Return a period defined by two dates.

    The order of start and end does not influence the result.
    """

    period_ends: List[dt.date] = sorted([period_start, period_end])
    start_day, end_day = period_ends

    period: List[dt.date] = []
    iterated_day = start_day
    while iterated_day <= end_day:
        period.append(iterated_day)
        iterated_day += dt.timedelta(days=1)

    return period


def is_continuous_period(period: List[dt.date]) -> bool:
    """Check if the period given is uninterrupted. Does not sort input list!"""
    if len(period) <= 1:
        return True

    for i in range(1, len(period)):
        if period[i - 1] + dt.timedelta(days=1) != period[i]:
            return False
    return True


class Color:
    """See https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit"""

    BLUE = 27
    GRAY = 242
    GREEN = 34
    ORANGE = 202
    RED = 9

    @staticmethod
    def color(text: str, clr_code: int, background: bool = False) -> str:
        """Color text with given color."""
        fg_bg_code = "38" if not background else "48"
        return Color._format(
            text=text, format_code="{};5;{}".format(fg_bg_code, clr_code)
        )

    @staticmethod
    def bold(text: str) -> str:
        """Format text as bold."""
        return Color._format(text=text, format_code="1")

    @staticmethod
    def _format(text: str, format_code: str) -> str:
        return "\x1b[{}m{}\x1b[0m".format(format_code, text)

    @staticmethod
    def clear(text: str) -> str:
        """Clear any applied escape sequences from the text."""
        return re.sub(r"\x1b\[[0-?]*[ -\/]*[@-~]", "", text)


class PrinTable:
    """Automatically justify strings in rows for a formatted table."""

    def __init__(self, padding: str = "") -> None:
        self.rows: List[List[str]] = []
        self.lines: Dict[int, str] = {}
        self.padding: str = padding

    def add_row(self, row: List[str]) -> None:
        """Add a row, represented as a list of column entries."""
        padded_row = [f"{self.padding}{cell}{self.padding}" for cell in row]
        self.rows.append(padded_row)

    def add_line(self, char: str) -> None:
        """Add a line, e.g. below a heading. Fills a row with the given char(s)."""
        self.lines[len(self.rows)] = char

    def printable(self) -> List[List[str]]:
        """Return rows with each cell left-justified to match the column width."""
        # Remove outer padding from first and last column
        unpadded_rows: List[List[str]] = [self._unpad_row(row) for row in self.rows]

        # Calculate column widths for printing
        col_widths: Counter = Counter()
        for row in unpadded_rows:
            for i, col in enumerate(row):
                # Clear the col of color codes before computing the string length
                col_widths[i] = max(col_widths[i], self._actual_len(col))

        # Return justified rows
        formatted_rows: List[List[str]] = []
        for row in unpadded_rows:
            formatted_row: List[str] = []
            for i, col in enumerate(row):
                delta_len: int = col_widths[i] - self._actual_len(col)
                formatted_row.append(col.ljust(len(col) + delta_len))
            formatted_rows.append(formatted_row)

        offset: int = 0
        for insert_idx, char in self.lines.items():
            line_row: List[str] = []
            for width in col_widths.values():
                line_row.append((width * char)[:width])
            formatted_rows.insert(insert_idx + offset, line_row)
            offset += 1

        return formatted_rows

    def _unpad_row(self, row: List[str]) -> List[str]:
        """Remove outer padding from first and last column."""
        if len(row) == 0:
            return row
        if len(row) == 1:
            return [remove_suffix(remove_prefix(row[0], self.padding), self.padding)]
        return [
            remove_prefix(row[0], self.padding),
            *row[1:-1],
            remove_suffix(row[-1], self.padding),
        ]

    def printable_str(self) -> List[str]:
        """
        Return rows justified (see `printable()`), but additionally combines the rows
        and trims excess space on the right.
        """
        return ["".join(row).rstrip() for row in self.printable()]

    @staticmethod
    def _actual_len(col: str) -> int:
        """The length of the string not counting escape sequences."""
        return len(Color.clear(col))

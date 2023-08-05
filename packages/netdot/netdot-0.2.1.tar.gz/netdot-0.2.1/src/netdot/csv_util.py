"""Classes and functions that generate CSV files.

This module is focused on generating a CSV file via the CSVReport class, which 
is a collections of CSVDataclass objects.
"""
import logging
import operator
import os
from typing import Generic, Iterable, List, Tuple, TypeVar, Union

import pathvalidate
from tabulate import tabulate

from . import io

logger = logging.getLogger(__name__)


class CSVDataclass:
    """Base class that provides a "table_header" class property 
    as well as a "as_table_row()" method for simple dataclasses.dataclass.
    """
    def table_header(self) -> Tuple[str, ...]:
        """Return the *names* from all attributes of this class.

        Returns:
            Tuple[str,...]: The names of the attributes for this class.
        """
        return tuple(self.__dataclass_fields__.keys())

    def as_table_row(self, select_columns: Iterable[str] = None) -> Tuple[str, ...]:
        """Return the data from all attributes of this object.

        Args:
            select_columns (Iterable[str], optional): Which data to be returned? If unset, all data returned.

        Returns:
            Tuple[str,...]: The values of all the attributes for this object.
        """
        obj_data = vars(self)
        if select_columns:
            row = tuple(obj_data[col] for col in select_columns)
        else:
            row = tuple(obj_data.values())
        row_as_strs = tuple(str(datum) for datum in row)
        return row_as_strs


CSVDataclass_t = TypeVar('CSVDataclass_t', bound=CSVDataclass)

class CSVReport(Generic[CSVDataclass_t]):
    """Base class for reports that can be exported to Comma Seperated Values (CSV).
    """
    def __init__(self, items: List[CSVDataclass_t], table_header: Tuple[str,...] = None):
        self._header: Tuple[str,...] = table_header
        self._items: List[CSVDataclass_t] = items
    
    @classmethod
    def ensure_not_overriding_custom_table_header(cls, kwargs):
        if 'table_header' in kwargs:
            raise ValueError(f'{cls} initializer overrides the "table_header" keyword argument.')

    def sort(self, sort_by: Union[str,Iterable[str]] = None):
        """Sort this report.

        Args:
            sort_by (Union[str,List[str]], optional): The column(s) to be sorted by. By default 
                will sort over all columns, from left-to-right.
        """
        if sort_by is None:
            sort_by = self.table_header()
        self.items.sort(key=operator.attrgetter(*sort_by))

    @property
    def items(self) -> List[CSVDataclass_t]:
        return self._items

    def table_header(self) -> Tuple[str, ...]:
        """Return the CSV header for this Report.

        Returns:
            Tuple[str,...]: Names of columns for this report.
        """
        if self._header: 
            return self._header
        else:
            try:
                return self.items[0].table_header()
            except IndexError:
                logger.error(f'Unable to determine table header for {self}. Returning empty list.')
                return []

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def as_tuples(self) -> List[Tuple]:
        return [
            self.row_formatting(item)
            for item in self.items
        ]

    def row_formatting(self, item: CSVDataclass_t) -> Tuple:
        columns = self.table_header()
        return item.as_table_row(select_columns=columns)

    # TODO, should this move out of this csv module/class?
    def as_table(self):
        return tabulate(self.as_tuples(), self.table_header())

    def as_csv(self, delim=',', override_header: Iterable[str] = None):
        """Produce this data structure into a CSV.

        Args:
            delim (str, optional): CSV delimeter to be used. Defaults to ','.
            override_header (Iterable[str], optional): Enables overriding the default CSV header. 
                Must be same length as this report's default `table_header`.

        Raises:
            ValueError: If override_header is invalid.

        Returns:
            str: This report, in CSV format.
        """        
        header = self.table_header()
        if override_header:
            if len(override_header) != len(header):
                raise ValueError(f'''CSV header must be length: {len(header)}.
                    Provided header length: {len(override_header)} (header: {override_header})''')
            header = override_header
        return as_csv(self.as_tuples(), header, delim)

    def save_as_file(self, filename: str, output_directory: str = './') -> int:
        """Save this CSVReport to a file.

        Args:
            output_directory (str): The path where the CSV will be saved.
            filename (str): Will be used as the file name.
            override_header (Iterable[str], optional): Enables overriding the default CSV header. 
                Must be same length as this report's default `table_header`.

        Returns:
            int: Amount of bytes written to the file. (See `TextIOBase.write()`)
        """
        io.ensure_directory_exist(output_directory)
        filename = _sanitize_csv_filename(filename)
        out_file_path = os.path.join(output_directory, filename)
        with open(out_file_path, 'w') as out_file:
            return out_file.write(self.as_csv())


def as_csv(data: Iterable[Tuple], header: Iterable[str] = None, delim=',') -> str:
    """Convert a list of tuples into a CSV table.

    Args:
        data (Iterable[Tuple]): The data tuples. Each tuple should be the same size, and the same size as the header.
        header (Iterable[str]): Header for the CSV table. Optional.
        delim (str, optional): CSV delimiter. Defaults to ','.

    Returns:
        str: The data, represented as a CSV.
    """
    csv_lines = []
    if header:
        csv_lines.append(delim.join(header))

    def sanitize(datum):
        return f'"{datum}"' if delim in str(datum) else str(datum)
    for line_data in data:
        line_data = list(map(sanitize, line_data))
        csv_lines.append(delim.join(line_data))

    return '\n'.join(csv_lines)


def _sanitize_csv_filename(filename: str) -> str:
    if not filename.endswith('.csv'):
        filename = f'{filename}.csv'
    return pathvalidate.sanitize_filename(filename)

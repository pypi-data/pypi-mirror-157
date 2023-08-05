import dataclasses
import textwrap

from assertpy import assert_that

from netdot.csv_util import CSVDataclass, as_csv


def test():
    headers = ['col1', 'col2', 'col3']
    data = [(1,2,3),(4,5,6)]

    # Act
    csv_string = as_csv(data, headers)

    # Assert
    assert_that(csv_string).contains(
        textwrap.dedent('''\
            col1,col2,col3
            1,2,3
            4,5,6''')
    )


def test_escape_delim():
    headers = ['sentence_col1', 'col2', 'col3']
    data = [('To be, or not to be,',2,3),('that is the question.',5,6)]

    # Act
    csv_string = as_csv(data, headers)

    # Assert
    assert_that(csv_string).contains("\"To be, or not to be,\"")


def test_csv_dataclass():
    # Arange & Act
    @dataclasses.dataclass
    class Foo(CSVDataclass):
        a: int

    # Assert
    foo = Foo(a=1)
    assert_that(foo.table_header()).is_equal_to(tuple(['a']))
    assert_that(foo.as_table_row()).is_equal_to(tuple(['1']))


def test_csv_dataclass_select_columns():
    # Arange & Act
    @dataclasses.dataclass
    class Foo(CSVDataclass):
        a: int
        b: int
        c: int
        d: int

    # Assert
    foo = Foo(a=1, b=2, c=3, d=4)
    data = foo.as_table_row(select_columns=['a', 'd'])
    assert_that(data).is_equal_to(tuple(['1','4']))

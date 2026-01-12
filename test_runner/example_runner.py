from collections import Counter
from decimal import Decimal
from test_runner.test_error import TestError
from test_runner.utils import print_red, print_green, indent
from test_runner.log_manager import LogManager
import traceback


def normalize_value_pair(expected, actual):
    """
    Normalize a value pair for comparison.
    - If actual is a float and expected is Decimal, convert Decimal to float (for REAL/DOUBLE PRECISION)
    - If actual is a string and expected is Decimal, convert Decimal to string (for NUMERIC/DECIMAL)
    - Otherwise, return both as-is
    """
    if isinstance(expected, Decimal):
        if isinstance(actual, float):
            return float(expected), actual
        elif isinstance(actual, str):
            return str(expected), actual
    return expected, actual


def normalize_rows(expected_rows, actual_rows):
    """Normalize rows pairwise based on actual value types."""
    normalized_expected = []
    normalized_actual = []
    
    for exp_row, act_row in zip(expected_rows, actual_rows):
        norm_exp = []
        norm_act = []
        for exp_val, act_val in zip(exp_row, act_row):
            ne, na = normalize_value_pair(exp_val, act_val)
            norm_exp.append(ne)
            norm_act.append(na)
        normalized_expected.append(tuple(norm_exp))
        normalized_actual.append(tuple(norm_act))
    
    return normalized_expected, normalized_actual


class TestComparisonError(Exception):
    def __init__(self, expected, result, example):
        self.expected = expected
        self.result = result
        self.example = example


class ResultIncorrectError(TestComparisonError):
    def __str__(self):
        actual = self.result['rows']
        order_string = "ordered" if self.example.ordered else "in any order"
        if self.expected == []:
            return ("Expected statement to return no rows\n"
                    "\n"
                    "Got rows:\n"
                    f"{indent(self.format_rows(actual))}")

        return (f"Expected statement to return rows ({order_string}):\n"
                f"{indent(self.format_rows(self.expected))}\n"
                "\n"
                "Got rows:\n"
                f"{indent(self.format_rows(actual))}")

    def format_rows(self, rows):
        formatted_rows = [
            ", ".join(map(self.format_value, row)) for row in rows
        ]
        return "\n".join(formatted_rows)

    def format_value(self, value):
        if value is True:
            return "TRUE"
        elif value is False:
            return "FALSE"
        elif value is None:
            return "NULL"
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, float):
            return str(value)
        elif isinstance(value, str):
            return f"'{self.escape_string(value)}'"
        else:
            raise ValueError(f"Unexpected value: {value}")

    def escape_string(self, value):
        return value.replace("\\", "\\\\").replace("'", "\\'")


class ColumnsIncorrectError(TestComparisonError):

    def __str__(self):
        actual = self.result['column_names']

        return (f"Expected statement to return columns:\n"
                f"  {self.format_columns(self.expected)}\n"
                "\n"
                "Got columns:\n"
                f"  {self.format_columns(actual)}"
                )

    def format_columns(self, columns):
        return ", ".join(columns)


class StatusIncorrectError(TestComparisonError):
    def __str__(self):
        actual = self.result['status']
        error_type = self.result.get('error_type', '')
        formatted_error_type = f" ({error_type})" if error_type else ""

        error_message = self.result.get('error_message')
        formatted_error_message = f"\n\nFull error message:\n{indent(error_message)}" if error_message else ""

        return f"Expected statement to return a status of '{self.expected}' but was '{actual}'{formatted_error_type}{formatted_error_message}"


class ErrorTypeIncorrectError(TestComparisonError):
    def __str__(self):
        actual = self.result['error_type']
        error_message = self.result.get('error_message')
        formatted_error_message = f"\n\nFull error message:\n{indent(error_message)}" if error_message else ""
        return f"Expected statement to return an error_type '{self.expected}' but was '{actual}'{formatted_error_message}"


class ExampleRunner():
    def __init__(self, suite, client):
        self.client = client
        self.suite = suite

    def run(self, example):
        self.queries_run = []

        try:
            self.run_example(example)
            for chained_example in example.chained_examples:
                self.run_example(chained_example)
            self.suite.record_pass(
                (example.file_name(), example.group_description, example.title))
            print_green('.', end='', flush=True)
            LogManager.print_logs()
        except TestComparisonError as e:
            print_red('F')
            LogManager.print_logs()
            print()
            example.print_summary()
            print(indent(str(e), 2))
            print()
            self.print_queries()
            self.suite.failure(rerun=example.rerun())
        except TestError as e:
            print_red('F')
            LogManager.print_logs()
            print()
            example.print_summary()
            print(indent(str(e), 2))
            print()
            self.print_queries()
            self.suite.failure(rerun=example.rerun())
        except Exception as e:
            print_red('E')
            LogManager.print_logs()
            print()
            example.print_summary()
            print(indent("An unexpected error has occurred:"))
            print(indent(str(traceback.format_exc()), 4))
            print()
            self.print_queries()
            self.suite.failure(rerun=example.rerun())

    def run_example(self, example):
        *setup_queries, query = example.sql

        for setup_query in setup_queries:
            result = self.run_query(setup_query)
            if result['status'] != 'ok':
                raise StatusIncorrectError('ok', result, example)

        result = self.run_query(query)

        if example.result != None:
            if result['status'] != 'ok':
                raise StatusIncorrectError('ok', result, example)
            if not self.result_matches(result, example):
                raise ResultIncorrectError(example.result, result, example)

        elif example.error:
            if result['status'] != 'error':
                raise StatusIncorrectError('error', result, example)
            if result['error_type'] != example.error:
                raise ErrorTypeIncorrectError(example.error, result, example)
        else:
            if result['status'] != 'ok':
                raise StatusIncorrectError('ok', result, example)

        if example.columns:
            if not self.columns_match(example.columns, result):
                raise ColumnsIncorrectError(example.columns, result, example)

    def print_queries(self):
        print(indent("Queries sent:"))
        for query in self.queries_run:
            print(indent(query, 4))
        print('')

    def run_query(self, query):
        self.queries_run.append(query)
        return self.client.run(query)

    def result_matches(self, result, example):
        if 'rows' not in result:
            raise TestError(
                f"Server response does not contain a 'rows' key")
        if example.result == []:
            return result['rows'] == [] or result['rows'] == [[]]
        
        # For unordered comparison with different row counts, fail fast
        if len(example.result) != len(result['rows']):
            return False
        
        # Normalize values pairwise based on actual types
        # This handles Decimal vs float (REAL) and Decimal vs string (NUMERIC)
        norm_expected, norm_actual = normalize_rows(example.result, result['rows'])
        
        if example.ordered:
            return norm_actual == norm_expected
        else:
            return Counter(norm_expected) == Counter(norm_actual)

    def columns_match(self, expected_columns, result):
        if 'column_names' not in result:
            raise TestError(
                f"Server response does not contain a 'column_names' key")
        return expected_columns == result['column_names']

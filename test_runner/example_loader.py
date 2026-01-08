import os
import glob
import re


from test_runner.example_parser import ExampleParser


def path_sort_key(path):
    file_name = os.path.basename(path)
    match = re.match(r'^(\d+)', file_name)
    if match:
        return [int(match.group(1)), file_name]
    else:
        return [float('inf'), file_name]





class ExampleLoader:
    def __init__(self, filtered_path, filtered_line, test_dir):
        self.filtered_path = filtered_path
        self.filtered_line = filtered_line
        self.test_dir = test_dir

    def examples(self):
        for path in self.filtered_paths():
            for example in self.load_examples(path):
                yield example

    def filtered_paths(self):
        sql_test_files = glob.glob(os.path.join(self.test_dir, '*.sql'))
        sql_test_files = sorted(sql_test_files, key=path_sort_key)

        if self.filtered_path:
            return [file for file in sql_test_files if os.path.samefile(file, self.filtered_path)]
        else:
            return sql_test_files

    def filter_to_line(self, examples, line):
        if not line:
            return examples

        before_line = list(filter(lambda e: e.line <= line, examples))
        if before_line:
            return [before_line[-1]]
        else:
            return [examples[0]]

    def load_examples(self, path):
        with open(path, 'r') as file:
            lines = file.readlines()

        examples = ExampleParser(path, lines).parse()
        return self.filter_to_line(examples, self.filtered_line)

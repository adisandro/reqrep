import csv
import os
from functools import cached_property


class TraceItem:
    def __init__(self, trace, row):
        self.trace = trace
        self.values = {k: float(row[i]) for k, i in trace.suite.variables.items()}


class Trace:
    def __init__(self, suite, path):
        self.suite = suite
        self.path = path
        self.items = []
        with open(self.path) as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    variables = {}
                    for j, var in enumerate(row):
                        variables[var] = j
                    if not suite.variables:
                        suite.variables = variables
                    else:
                        if suite.variables != variables:
                            raise ValueError("Trace variables do not match across traces.")
                    continue
                self.items.append(TraceItem(self, row))


class TraceSuite:
    def __init__(self, path, prev0):
        self.prev0 = prev0
        self.traces = []
        self.variables = {}
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir() or not entry.name.endswith('.csv'):
                    continue
                entry_trace = Trace(self, entry.path)
                self.traces.append(entry_trace)

    @cached_property
    def variable_names(self):
        return sorted([v for v in self.variables if v != "Time"])

import csv
import os
from collections import namedtuple
from functools import cached_property


class TraceItem:
    def __init__(self, trace, row):
        self.trace = trace
        self.values = {}
        for i, (k, v) in enumerate(trace.suite.variables.items()): # dict keeps insertion order
            value = float(row[i])
            self.values[k] = value
            if v["min"] is None or value < v["min"]:
                v["min"] = value
            if v["max"] is None or value > v["max"]:
                v["max"] = value

    @cached_property
    def time(self):
        return self.values[self.trace.suite.TIME_VAR]


class Trace:
    def __init__(self, suite, path):
        self.suite = suite
        self.path = path
        self.items = []
        with open(self.path) as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    variables = {var.partition("|")[0]: {"unit": var.partition("|")[2], "min": None, "max": None}
                                 for var in row}
                    if not suite.variables:
                        if not suite.in_variable_names.issubset(variables.keys()):
                            raise ValueError("Input variables not found")
                        suite.variables = variables
                    else:
                        if suite.variables.keys() != variables.keys():
                            raise ValueError("Trace variables do not match across traces")
                    continue
                self.items.append(TraceItem(self, row))

Variable = namedtuple("Variable", ["unit", "min", "max"])
class TraceSuite:
    TIME_VAR = "Time"

    def __init__(self, path, in_variable_names, prev0):
        self.in_variable_names = in_variable_names
        self.prev0 = prev0
        self.traces = []
        self.variables = {}
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir() or not entry.name.endswith('.csv'):
                    continue
                self.traces.append(Trace(self, entry.path))

    @cached_property
    def variable_names(self):
        # Start with in_variable_names, then add the rest (excluding TIME_VAR and already included)
        rest = [v for v in self.variables if v != self.TIME_VAR and v not in self.in_variable_names]
        return list(self.in_variable_names) + sorted(rest)

import csv
import os


class TraceItem:
    def __init__(self, row, trace):
        self.values = {k: row[i] for k, i in trace.variables.items()}


class Trace:
    def __init__(self, path):
        self.path = path
        self.variables = {}
        self.items = []
        with open(self.path) as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    for j, var in enumerate(row):
                        self.variables[var] = j
                    continue
                self.items.append(TraceItem(row, self))


class TraceSuite:
    def __init__(self, path):
        self.traces = []
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir() or not entry.name.endswith('.csv'):
                    continue
                self.traces.append(Trace(entry.path))

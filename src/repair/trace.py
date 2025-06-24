import csv
from collections import defaultdict


class TraceItem:
    def __init__(self, row, trace):
        self.trace = trace
        self.values = {k: row[i] for k, i in trace.variables.items()}
        self.pre_pass = {}
        self.post_pass = {}

    def evaluate(self, requirements, transformations):
        for req in requirements:
            req.check(self)
            for trans in transformations:
                req_trans = trans.apply(req)
                if self.pre_pass[req.name] and self.post_pass[req.name]:
                    self.trace.pre_pass_perc.setdefault(req_trans.name, 0)
                    self.trace.pre_pass_perc[req_trans.name] += 1
                    self.trace.post_pass_perc.setdefault(req_trans.name, 0)
                    self.trace.post_pass_perc[req_trans.name] += 1
                else:
                    req_trans.check(self)

    def __repr__(self):
        out = f'Time {self.values["Time"]}:\n'
        for name, pre_res in self.pre_pass.items():
            out += f'\tPRE {'✔' if pre_res else '✘'} POST {'✔' if self.post_pass[name] else '✘'} [{name}]\n'
        return out


class Trace:
    def __init__(self, path):
        self.path = path
        self.variables = {}
        self.items = []
        self.pre_pass_perc = {}
        self.post_pass_perc = {}

    def parse(self):
        with open(self.path) as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    for j, var in enumerate(row):
                        self.variables[var] = j
                    continue
                self.items.append(TraceItem(row, self))

    def evaluate(self, reqs, transforms):
        for item in self.items:
            item.evaluate(reqs, transforms)
        num_items = len(self.items)
        for name in self.pre_pass_perc.keys():
            self.pre_pass_perc[name] /= num_items
        for name in self.post_pass_perc.keys():
            self.post_pass_perc[name] /= num_items

    def __repr__(self):
        out = f'Trace: {self.path}\n'
        for item in self.items:
            out += item.__repr__()
        for name, perc in self.pre_pass_perc.items():
            out += f'PRE {perc*100}% [{name}]\n'
        for name, perc in self.post_pass_perc.items():
            out += f'POST {perc*100}% [{name}]\n'
        return out

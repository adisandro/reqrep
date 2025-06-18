import csv


class Requirement:
    def __init__(self, name, precondition, postcondition):
        self.name = name
        self.precondition = precondition
        self.postcondition = postcondition

    def check(self, trace):
        if self.precondition(trace.variables):
            if self.postcondition(trace.variables):
                return 'postcondition met'
            else:
                return 'postcondition not met'
        return 'precondition not met'


class Trace:
    def __init__(self, path):
        self.path = path
        self.variables = {}

    def parse(self, reqs):
        with open(self.path) as csvfile:
            print(f'Trace: {self.path}')
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    for j, var in enumerate(row):
                        self.variables[var] = j
                    continue
                print(f'Time {row[self.variables["Time"]]}:')
                for req in reqs:
                    result = req.check(self)
                    print(f'\tReq {req.name} {result}')

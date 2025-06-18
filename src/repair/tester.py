import csv


class Requirement:
    def __init__(self, name, precondition, postcondition):
        self.name = name
        self.precondition = precondition
        self.postcondition = postcondition

    def check(self, values):
        pre = self.precondition
        post = self.postcondition
        for var, value in values.items():
            pre = pre.replace(var, value)
            post = post.replace(var, value)
        if eval(pre):
            if eval(post):
                return 'postcondition met'
            else:
                return 'postcondition not met'
        return 'precondition not met'


class Transformation:
    def __init__(self, name, transform_pre, transform_post):
        self.name = name
        self.transform_pre = transform_pre
        self.transform_post = transform_post

    def apply(self, requirement):
        return Requirement(requirement.name + ' + ' + self.name, self.transform_pre(requirement.precondition),
                           self.transform_post(requirement.postcondition))


class Trace:
    def __init__(self, path):
        self.path = path
        self.variables = {}

    def parse(self, reqs, transforms):
        with open(self.path) as csvfile:
            print(f'Trace: {self.path}')
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    for j, var in enumerate(row):
                        self.variables[var] = j
                    continue
                print(f'Time {row[self.variables["Time"]]}:')
                values = {k: row[i] for k, i in self.variables.items()}
                for req in reqs:
                    result = req.check(values)
                    # TODO: return something different than a string result to execute transformation
                    # TODO: cache transformed requirements?
                    print(f'\tReq {req.name} {result}')
                    for trans in transforms:
                        req_trans = trans.apply(req)
                        result2 = req_trans.check(values)
                        print(f'\tReq {req_trans.name} {result2}')

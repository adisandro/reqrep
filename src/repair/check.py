class Requirement:
    def __init__(self, name, precondition, postcondition):
        self.name = name
        self.precondition = precondition
        self.postcondition = postcondition

    def check(self, item):
        pre = self.precondition
        post = self.postcondition
        for var, value in item.values.items():
            pre = pre.replace(var, value)
            post = post.replace(var, value)
        item.pre_pass[self.name] = True if eval(pre) else False
        item.trace.pre_pass_perc.setdefault(self.name, 0)
        if item.pre_pass[self.name]:
            item.trace.pre_pass_perc[self.name] += 1
        item.post_pass[self.name] = True if item.pre_pass[self.name] and eval(post) else False
        item.trace.post_pass_perc.setdefault(self.name, 0)
        if item.post_pass[self.name]:
            item.trace.post_pass_perc[self.name] += 1


class Transformation:
    def __init__(self, name, transform_pre, transform_post):
        self.name = name
        self.transform_pre = transform_pre
        self.transform_post = transform_post

    def apply(self, requirement):
        return Requirement(requirement.name + ' + ' + self.name, self.transform_pre(requirement.precondition),
                           self.transform_post(requirement.postcondition))

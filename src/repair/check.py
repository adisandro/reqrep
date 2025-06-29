from random import choice


class Requirement:
    def __init__(self, precondition, postcondition):
        self.precondition = precondition
        self.postcondition = postcondition
        self.pre_pass_ts = 0
        self.pre_pass_t = {}
        self.post_pass_ts = 0
        self.post_pass_t = {}

    def check(self, item):
        pre = self.precondition
        post = self.postcondition
        for var, value in item.values.items():
            pre = pre.replace(var, value)
            post = post.replace(var, value)
        pre_pass = True if eval(pre) else False
        post_pass = True if pre_pass and eval(post) else False
        return pre_pass, post_pass

    def eval_correctness(self, trace_suite):
        self.pre_pass_ts = 0
        self.post_pass_ts = 0
        all_items = 0
        for trace in trace_suite.traces:
            pre_pass_t = 0
            post_pass_t = 0
            for item in trace.items:
                pre_pass, post_pass = self.check(item)
                if pre_pass:
                    pre_pass_t += 1
                if post_pass:
                    post_pass_t += 1
            all_items += len(trace.items)
            self.pre_pass_t[trace.path] = pre_pass_t / len(trace.items)
            self.pre_pass_ts += pre_pass_t
            self.post_pass_t[trace.path] = post_pass_t / len(trace.items)
            self.post_pass_ts += post_pass_t
        self.pre_pass_ts /= all_items
        self.post_pass_ts /= all_items

    def repair(self, trace_suite, transformations):
        req_cur = self
        fitness = {}
        while True:
            req_cur.eval_correctness(trace_suite)
            print(req_cur)
            if req_cur.post_pass_ts == 1:
                break
            req_cur = choice(transformations).apply(req_cur)

    def __repr__(self):
        out = f'PRE: {self.precondition}\nPOST: {self.postcondition}\n'
        out += f'TraceSuite: PRE {self.pre_pass_ts*100}% POST {self.post_pass_ts*100}%\n'
        for path, pre_res in self.pre_pass_t.items():
            out += f'\tTrace {path}: PRE {pre_res*100} POST {self.post_pass_t[path]*100}\n'
        return out


class Transformation:
    def __init__(self, name, transform_pre, transform_post):
        self.name = name
        self.transform_pre = transform_pre
        self.transform_post = transform_post

    def apply(self, requirement):
        return Requirement(self.transform_pre(requirement.precondition), self.transform_post(requirement.postcondition))

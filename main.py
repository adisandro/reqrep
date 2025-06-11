import csv


def requirement(variables, precondition, postcondition):
    if precondition(variables):
        if postcondition(variables):
            return 'postcondition met'
        else:
            return 'postcondition not met'
    return 'precondition not met'

def main():
    # TODO: Do we care which are inputs and which are outputs?
    reqs = [
        {'name': '1',
         'pre': lambda v: v['BL'] <= v['ic'] <= v['TL'] and v['reset'] == 0,
         'post': lambda v: v['yout'] == v['ic']},
        {'name': '2',
         'pre': lambda v: True,
         'post': lambda v: v['TL'] >= v['yout'] >= v['BL']},
    ]
    with open('samples/TUI_0001.csv') as csvfile:
        reader = csv.reader(csvfile)
        variables = {}
        for i, row in enumerate(reader):
            if i == 0:
                for j, var in enumerate(row):
                    variables[var] = j
                continue
            print(f'Time {row[variables["Time"]]}:')
            for req in reqs:
                result = requirement(variables, req['pre'], req['post'])
                print(f'\tReq {req['name']} {result}')

if __name__ == "__main__":
    main()
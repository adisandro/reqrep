import os
import random
import pandas as pd
import matplotlib.pyplot as plt

from repair.approach.approach import Approach
from repair.approach.trace import Trace, TraceSuite  # Reuse the Trace class
from repair.fitness.correctness.utils import get_trace_correctness
from utils import REQUIREMENTS, INPUT_VARIABLES

OUTPUT_FOLDER = "output/figures"

class DummyApproach(Approach):
    
    def __init__(self, trace_suite, requirement_text, iterations, desirability):
        super().__init__(trace_suite, requirement_text, iterations, desirability)

    def repair(self, threshold):
        pass

def filter_traces(traces, requirement):
    # Placeholder: implement actual requirement logic as needed
    # For now, just return all traces
    return traces

def plot_trace(trace, violating_indices, output_folder, trace_name="trace", requirement_line=None):
    os.makedirs(output_folder, exist_ok=True)

    # Create a DataFrame from trace.items
    data = [item.values for item in trace.items]
    df = pd.DataFrame(data)

    # Plot each variable separately
    for var in trace.suite.variables:
        if var == 'Time':
            continue
        plt.figure()
        plt.plot(df['Time'], df[var], label=var, color='blue')

        # Highlight violating indices in red
        if violating_indices:
            violating_times = df['Time'].iloc[violating_indices]
            violating_values = df[var].iloc[violating_indices]
            plt.plot(violating_times, violating_values, color='red', label='Violation', linewidth=2, zorder=5)
            # plt.scatter(violating_times, violating_values, color='red', label='Violation', zorder=5, s=5)

        #show requirement
        if requirement_line is not None:
            plt.hlines(y=requirement_line, xmin=0, xmax=10, color='black', linestyle='--', linewidth=1, label='requirement')

        plt.xlabel('Time')
        plt.ylabel(var)
        plt.title(f'{var} vs Time')
        plt.legend(loc='lower right')
        var_type = "in" if var in trace.suite.in_variable_names else "out"
        output_path = os.path.join(output_folder, f"{trace_name}_{var_type}_{var}.png")
        plt.savefig(output_path)
        plt.close()
        print(f"Saved plot to {output_path}")


def process_traces(folder_path, requirement, in_variable_names, output_folder, requirement_line=None):
    # make Trace suite
    traceSuite = TraceSuite(folder_path, in_variable_names, -1)
    approach = DummyApproach(traceSuite, requirement, -1, None)

    init_req = approach.init_requirement
    # print(init_req.to_str(trace_suite=traceSuite))

    df_cor = get_trace_correctness(init_req.pre, init_req.post, traceSuite)

    # Filter out all rows where delta_cor == 0
    df_cor = df_cor[df_cor["delta_cor"] != 0]
    df_cor = df_cor.sort_values(by=["delta_cor", "perc_cor"], ascending=[False, True]).reset_index(drop=True)
    print(df_cor)

    # Select the first row (most violating trace)
    if not df_cor.empty:
        selected_df_entry = df_cor.iloc[0]
        first_id = selected_df_entry["trace_index"]
        violating_indices = selected_df_entry["violating_indices"]
        selected_trace = traceSuite.traces[int(first_id)]
        trace_name = f"{os.path.basename(folder_path.rstrip(os.sep))}_most_violating"
        plot_trace(selected_trace, violating_indices, output_folder, trace_name=trace_name, requirement_line=requirement_line)


if __name__ == "__main__":

    folder = "data/case_studies/AT-AT2"
    custom = 4650
    in_variable_names = INPUT_VARIABLES[folder]  # Define input variable names as needed
    if custom:
        requirement = (
        "and("
            "and(ge(Throttle, 5.0), le(Throttle, 100.0)),"
            "and(ge(Brake, 0.0),    le(Brake, 325.0)))",
        f"dur(0, 10, lt(Engine, {custom}.0))"
    )
    else:
        requirement = REQUIREMENTS[folder]
    process_traces(folder, requirement, in_variable_names, OUTPUT_FOLDER, custom)

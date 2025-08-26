import os
import random
import pandas as pd
import matplotlib.pyplot as plt

from repair.approach.approach import Approach
from repair.approach.trace import Trace, TraceSuite  # Reuse the Trace class
from repair.fitness.correctness.utils import get_trace_correctness
from utils import REQUIREMENTS, INPUT_VARIABLES

OUTPUT_FOLDER = "output/figures"

LABELS = {
    "Engine": "Engine Speed (rpm)",
    "Throttle": "Throttle Signal (%)",
    "Brake": "Brake Torque (lb*ft)"
}

class DummyApproach(Approach):
    
    def __init__(self, trace_suite, requirement_text, iterations, desirability):
        super().__init__(trace_suite, requirement_text, iterations, desirability)

    def repair(self, threshold):
        pass

def plot_trace(traces, violating_indices_list, output_folder, trace_name="trace", requirement_line=None, accepted_vars=None, line_color='blue', y_lb=None, dims=(3.33, 2.5), add_legend=False):
    os.makedirs(output_folder, exist_ok=True)

    # Create a DataFrame from trace.items
    dfs = []
    for trace in traces:
        data = [item.values for item in trace.items]
        df = pd.DataFrame(data)
        dfs.append(df)

    # Print the first DataFrame to a file for inspection
    if len(traces) == 1:
        dfs[0].to_csv(os.path.join(output_folder, f"{trace_name}_trace.csv"), index=False)

    # Plot each variable separately
    for var in traces[0].suite.variables:
        if var == 'Time':
            continue
        if accepted_vars is not None and var not in accepted_vars:
            continue
        plt.figure()
        fig, ax = plt.subplots(figsize=dims)
        for i, (df, violating_indices) in enumerate(zip(dfs, violating_indices_list)):
            ax.plot(df['Time'], df[var], label=f"Trace {i}", color=line_color)

            if requirement_line is not None and var == requirement_line[0]:

                # Highlight violating indices in red
                if violating_indices:
                    violating_times = df['Time'].iloc[violating_indices]
                    violating_values = df[var].iloc[violating_indices]
                    plt.plot(violating_times, violating_values, color='red', linewidth=2, zorder=5)
                    # plt.scatter(violating_times, violating_values, color='red', label='Violation', zorder=5, s=5)
                
                #show requirement
                ax.hlines(y=requirement_line[1], xmin=0, xmax=10, color='black', linestyle='--', linewidth=1)

        ax.set_xlabel('Time (s)')
        ax.set_ylabel(var if var not in LABELS else LABELS[var])
        ax.set_ylim(bottom=y_lb)
        # fig.title(f'{var} vs Time')

        fig.tight_layout()
        if add_legend:
            fig.legend()
        var_type = "in" if var in trace.suite.in_variable_names else "out"
        output_path = os.path.join(output_folder, f"{trace_name}_{var_type}_{var}.png")
        fig.savefig(output_path)
        plt.close()
        print(f"Saved plot to {output_path}")


def process_traces(folder_path, requirement, in_variable_names):
    # make Trace suite
    traceSuite = TraceSuite(folder_path, in_variable_names, -1)
    approach = DummyApproach(traceSuite, requirement, -1, None)
    # print(traceSuite.traces[68].items[150].values)

    init_req = approach.init_requirement
    # print(init_req.to_str(trace_suite=traceSuite))

    # Get best trace
    df_cor = get_trace_correctness(init_req.pre, init_req.post, traceSuite)

    return traceSuite, df_cor

def prep_best_plots(traceSuite, df_cor, folder_path, output_folder, requirement_line=None):

    # Filter out all rows where delta_cor == 0
    df_cor = df_cor[df_cor["delta_cor"] != 0]
    df_cor = df_cor.sort_values(by=["delta_cor", "perc_cor"], ascending=[False, True]).reset_index(drop=True)
    print(df_cor)
    # Print the violating_times column for each violating trace
    for idx, row in df_cor.iterrows():
        violating_indices = row["violating_indices"]
        trace_index = row["trace_index"]
        trace = traceSuite.traces[int(trace_index)]
        data = [item.values for item in trace.items]
        df = pd.DataFrame(data)
        violating_times = df['Time'].iloc[violating_indices]
        violating_values = df['Engine'].iloc[violating_indices]
        print(f"Trace {trace_index} violating_times: {violating_times.values}")
        print(f"                    violating_values: {violating_values.values}")

    # Plot the first row (most violating trace)
    if not df_cor.empty:
        selected_df_entry = df_cor.iloc[0]
        first_id = selected_df_entry["trace_index"]
        violating_indices = selected_df_entry["violating_indices"]
        selected_trace = traceSuite.traces[int(first_id)]
        trace_name = f"{os.path.basename(folder_path.rstrip(os.sep))}_most_violating"
        plot_trace([selected_trace], [violating_indices], output_folder, trace_name=trace_name, requirement_line=requirement_line)


def prep_other_plots(traceSuite, df_cor, more_traces_to_show, folder_path, output_folder, requirement_line=None):

    # Create additional plots (output only) for more traces
    for trace_indices in more_traces_to_show:
        traces_to_show = []
        violating_indices_to_show = []

        for trace_index in trace_indices:
            trace_to_show = traceSuite.traces[trace_index]
            # print(max([item.values['Engine'] for item in trace_to_show.items]))
            # Find the df_cor entry for this trace_index to get violating_indices
            df_entry = df_cor[df_cor["trace_index"] == trace_index]
            violating_indices = [] if df_entry.empty else  df_entry.iloc[0]["violating_indices"]
            traces_to_show.append(trace_to_show)
            violating_indices_to_show.append(violating_indices)

        trace_name = f"{os.path.basename(folder_path.rstrip(os.sep))}_trace_{trace_indices}"
        plot_trace(traces_to_show, violating_indices_to_show, output_folder,
                    trace_name=trace_name,
                    requirement_line=requirement_line,
                    accepted_vars=["Engine"],
                    line_color=None,
                    y_lb=3000,
                    dims=(6, 2.5),
                    add_legend=True
                    )


if __name__ == "__main__":

    traces_to_show = [[1, 2, 3], # random
                      [68, 82, 27], # violations
                    #   [68] # Worst one
                      ]

    folder = "data/case_studies/AT-AT2"
    custom = ("Engine", 4650)
    in_variable_names = INPUT_VARIABLES[folder]  # Define input variable names as needed
    if custom:
        requirement = (
        "and("
            "and(ge(Throttle, 5.0), le(Throttle, 100.0)),"
            "and(ge(Brake, 0.0),    le(Brake, 325.0)))",
        f"dur(0, 10, lt(Engine, {custom[1]}.0))"
    )
    else:
        requirement = REQUIREMENTS[folder]
    ts, df_cor = process_traces(folder, requirement, in_variable_names)
    prep_best_plots(ts, df_cor, folder, OUTPUT_FOLDER, requirement_line=custom)
    prep_other_plots(ts, df_cor, traces_to_show, folder, OUTPUT_FOLDER, requirement_line=custom)

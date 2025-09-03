import os
import pandas as pd
import matplotlib.pyplot as plt

from repair.approach.approach import Approach
from repair.approach.optimization.optimization import OptimizationApproach
from repair.approach.requirement import Requirement
from repair.approach.trace import TraceSuite  # Reuse the Trace class
from repair.fitness.correctness.utils import get_trace_correctness
from repair.fitness.desirability.applicabilitypreservation import SatisfiedTimestepDifference
from repair.fitness.desirability.desirability import Desirability
from repair.fitness.desirability.semanticsanity import SamplingBasedSanity
from repair.fitness.desirability.syntacticsimilarity import CosineSimilarity
from utils import REQUIREMENTS, INPUT_VARIABLES

OUTPUT_FOLDER = "output/figures2"

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

def plot_trace(traces, violating_indices_list, 
               output_folder, trace_name="trace",
               requirement_line=None, accepted_vars=None,
               line_color='blue', y_ranges=None,
               dims=(3.33, 2.5), add_legend=False):
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

            if requirement_line is not None:

                # Highlight violating indices in red
                if violating_indices:
                    violating_times = df['Time'].iloc[violating_indices]
                    violating_values = df[var].iloc[violating_indices]
                    plt.plot(violating_times, violating_values, color='red', linewidth=2, zorder=5)
                    # plt.scatter(violating_times, violating_values, color='red', label='Violation', zorder=5, s=5)
                
                if var in requirement_line:
                    for i, r_line in enumerate(requirement_line[var]):
                        #show requirement
                        if isinstance(r_line, tuple):
                            r_val, r_color, r_style = r_line
                            ax.hlines(y=r_val, xmin=0, xmax=10, color=r_color, linestyle=r_style, linewidth=1) #, label=f"Req {r_val}")
                        else:
                            ax.hlines(y=r_line, xmin=0, xmax=10, linewidth=1)

        ax.set_xlabel('Time (s)')
        ax.set_ylabel(var if var not in LABELS else LABELS[var])
        # ax.set_ylim(bottom=y_lb)
        if y_ranges:
            y_lb, y_ub = y_ranges.get(var, (None, None))
            ax.set_ylim(y_lb, y_ub)  # Set y-axis range from 0 to 100
        # fig.title(f'{var} vs Time')

        fig.tight_layout()
        if add_legend:
            fig.legend()
        var_type = "in" if var in trace.suite.in_variable_names else "out"
        output_path = os.path.join(output_folder, f"{trace_name}_{var_type}_{var}.png")
        fig.savefig(output_path)
        plt.close()
        print(f"Saved plot to {output_path}")


def process_traces(folder_path, requirement, in_variable_names, ids_to_include=None):
    # make Trace suite
    traceSuite = TraceSuite(folder_path, in_variable_names, -1)

    if ids_to_include is not None:
        traceSuite.traces = [traceSuite.traces[i] for i in ids_to_include]

    d = Desirability(
        trace_suite=traceSuite,
        semantic=SamplingBasedSanity(n_samples=10),
        syntactic=CosineSimilarity(),
        applicability=SatisfiedTimestepDifference(),
        weights=[1.0, 1.0, 1.0]
    )

    # Define APPROACH
    approach = OptimizationApproach(traceSuite, requirement, -1, d)
    # print(traceSuite.traces[68].items[150].values)

    init_req = approach.init_requirement
    # print(init_req.to_str(trace_suite=traceSuite))

    # Get best trace
    df_cor = get_trace_correctness(init_req.pre, init_req.post, traceSuite)

    return traceSuite, df_cor, approach

def print_trace(trace, index, show_dur=False):
    print(f"Trace {index}:")
    # Compile the first 30 entries into a DataFrame
    data = [item.values for item in trace.items]
    df = pd.DataFrame(data)

    if show_dur and "Time" in df.columns:
        
        window_seconds = 2.56  # Set the window size as a variable
        lb = 96.3145893897216
        ub = 100
        # Add a column that stores the running minimum of the previous rows within window_seconds for "Throttle"
        running_min = []
        times = df["Time"].values
        throttle = df["Throttle"].values
        for i in range(len(df)):
            # Find indices of previous rows where time is within window_seconds of current row (excluding current row)
            mask = (times[:i] >= times[i] - window_seconds)
            if i > 0 and mask.any():
                m = throttle[:i][mask].min()
                running_min.append(-(min(-lb+m, -m+ub)))
            else:
                running_min.append(None)
        df[f"Throttle_running_min_{window_seconds}s"] = running_min

        plt.figure(figsize=(8, 3))
        plt.plot(df["Time"], df[f"Throttle_running_min_{window_seconds}s"], label=f"Throttle_running_min_{window_seconds}s", color="orange")
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1)  # Show axis at y=0
        plt.xlabel("Time (s)")
        plt.ylabel(f"Throttle Running Min ({window_seconds}s)")
        plt.title(f"Trace {index} - Throttle Running Min ({window_seconds}s)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"output/trace_{index}_throttle_running_min.png")
        plt.close()

        df.to_csv(f"output/trace_{index}_full.csv", index=False)

    # Round all float columns to 3 decimal places
    if 'Time' in df.columns:
        df['Time'] = df['Time'].round(2)
    float_cols = [col for col in df.select_dtypes(include=['float']).columns if col != 'Time']
    df[float_cols] = df[float_cols].round(3)

    print(df.head(30))


def prep_best_plots(traceSuite, df_cor, folder_path, output_folder):

    y_ranges = {"Engine": (None, None),
                "Throttle": (None, None),
                "Brake": (None, None)}

    requirement_line = {"Engine": [(4650, 'black', '--'), (4764.86, 'green', '-.')],
                        "Throttle": [(100, 'black', '--'), (96.34, 'purple', '-.')],
                        "Brake": [(325, 'black', '--')]}

    # Filter out all rows where delta_cor == 0
    df_cor = df_cor[df_cor["delta_cor"] != 0]
    df_cor = df_cor.sort_values(by=["delta_cor", "perc_cor"], ascending=[False, True]).reset_index(drop=True)
    # print(df_cor)
    # Print the violating_times column for each violating trace
    for idx, row in df_cor.iterrows():
        violating_indices = row["violating_indices"]
        trace_index = row["trace_index"]
        trace = traceSuite.traces[int(trace_index)]
        data = [item.values for item in trace.items]
        df = pd.DataFrame(data)
        violating_times = df['Time'].iloc[violating_indices]
        violating_values_engine = df['Engine'].iloc[violating_indices]
        violating_values_throttle = df['Throttle'].iloc[violating_indices]
        print(f"Trace {trace_index}")
        print(f"    violating_times: {violating_times.values}")
        print(f"    violating_values_engine: {violating_values_engine.values}")
        print(f"    violating_values_throttle: {violating_values_throttle.values}")

    # Plot the first row (most violating trace)
    if not df_cor.empty:
        selected_df_entry = df_cor.iloc[0]
        first_id = selected_df_entry["trace_index"]
        violating_indices = selected_df_entry["violating_indices"]
        selected_trace = traceSuite.traces[int(first_id)]
        trace_name = f"{os.path.basename(folder_path.rstrip(os.sep))}_most_violating"
        print_trace(selected_trace, first_id, True) # True is temporary
        plot_trace([selected_trace], [violating_indices], output_folder, trace_name=trace_name, requirement_line=requirement_line, y_ranges=y_ranges)


def prep_other_plots(traceSuite, df_cor, more_traces_to_show, folder_path, output_folder):

    # requirement_line = {"Engine": [4650, 4760, 4780, 4800]}
    requirement_line = {"Engine": [(4650, 'black', '--'), (4800, 'purple', '-.')],
                        "Throttle": [(100, 'black', '--'), (92, 'purple', '-.')]}

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
                    accepted_vars=["Engine", "Throttle"],
                    line_color=None,
                    y_ranges={"Engine": (3000, None), "Throttle": (50, None)},
                    dims=(6, 2.5),
                    add_legend=True
                    )


def print_des_of_other(folder, in_variable_names, traces_to_show):

    requirements = [
                ("and(ge(Throttle, 0.0), le(Throttle, 98.0))",
                 "lt(Engine, 4650.0)"), # INITIAL
                ("and(ge(Throttle, 0.0), le(Throttle, 98.0))",
                 "lt(Engine, 4800.0)"), # SYN
                ("and(ge(Throttle, 0.0), le(Throttle, 98.0))",
                 "lt(Engine, add(Engine, 1.0))") # TAUT
    ]
    # TODO add a couple more examples

    for trace_indices in traces_to_show:
        traceSuite, df_cor, approach = process_traces(folder, requirements[0], in_variable_names, trace_indices)

        for i, r_text in enumerate(requirements):
            r = Requirement(f"r_{i}", approach.toolbox,
                        approach.pset_pre, r_text[0],
                        approach.pset_post, r_text[1])
            
            print(r.to_str(trace_suite=traceSuite))


if __name__ == "__main__":

    traces_to_show = [[1, 2, 3], # random
                      [68, 82, 27], # violations
                    #   [68] # Worst one
                      ]
    
    # traces_to_show = [[68]]    
    traces_to_show = [[68, 82, 27]]

    folder = "data/case_studies/AT-AT2"
    custom = {"Engine": [4650, 4764.86],
              "Throttle": [100, 96.34]}
    in_variable_names = INPUT_VARIABLES[folder]  # Define input variable names as needed
    if custom:
        requirement = (
        "and("
            "and(ge(Throttle, 5.0), le(Throttle, 100.0)),"
            "and(ge(Brake, 0.0),    le(Brake, 325.0)))",
        "dur(0, 10, lt(Engine, 4650.0))"
    )
    else:
        requirement = REQUIREMENTS[folder]
    ts, df_cor, _ = process_traces(folder, requirement, in_variable_names)
    prep_best_plots(ts, df_cor, folder, OUTPUT_FOLDER)
    prep_other_plots(ts, df_cor, traces_to_show, folder, OUTPUT_FOLDER)

    print_des_of_other(folder, in_variable_names, traces_to_show)

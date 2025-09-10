#!/usr/bin/env python3
import pandas as pd

def rq2(case_studies, data):
    data = data[data["aggregation_strategy"] == "no_aggregation"]
    correct = data[
        (data["f_correctness"] > 0) &
        (data["f_des_semantic"] > 0)
    ].sort_values(by=["f_des_syntactic", "f_des_satisfaction"])
    for case_study, requirements in case_studies.items():
        all = data[data["config_id"].str.startswith(case_study)]
        good = correct[correct["config_id"].str.startswith(case_study)]
        print(f"{case_study} & {round(len(good)/len(all), 2)} \\\\")

if __name__ == "__main__":
    data = pd.read_csv("output/results.csv")
    case_studies = {"AFC": ["AFC29", "AFC33"], "AT": ["AT1", "AT2"], "CC": ["CC1", "CCX"], "EU": ["EU3"],
                    "NNP": ["NNP3a", "NNP3b", "NNP4"], "TUI": ["TU1", "TU2"]}
    rq2(case_studies, data)
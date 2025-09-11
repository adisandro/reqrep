#!/usr/bin/env python3
import math

import pandas as pd

def is_zero(x):
    return math.isclose(x, 0.0, abs_tol=1e-6)

def rq2(case_studies, data):
    data = data[(data["aggregation_strategy"] == "no_aggregation") & data["config_id"].str.endswith("111")]
    correct_data = (data[(data["f_correctness"].apply(is_zero)) & (data["f_des_semantic"].apply(is_zero))]
                    .sort_values(by=["f_des_syntactic", "f_des_satisfaction"]))
                    # .sort_values(by=["f_des_satisfaction", "f_des_syntactic"]))
    repairs = "\n"
    for case_study in case_studies:
        case_data = data[data["config_id"].str.startswith(case_study)]
        case_correct_data = correct_data[correct_data["config_id"].str.startswith(case_study)]
        ratio = round(len(case_correct_data)/len(case_data), 2)
        print(f"{case_study} & {ratio} &  &  &  & \\\\")
        for i in range(10):
            repair = case_correct_data.iloc[i]
            repair_req = repair["config_id"].split("_")[1]
            repair_pre = repair["precondition"].replace("_", "\\_")
            repair_post = repair["postcondition"].replace("_", "\\_")
            repair_syn = round(repair["f_des_syntactic"], 2)
            repair_sat = round(repair["f_des_satisfaction"], 2)
            repairs += f"\\item[{repair_req}] {repair_pre} => {repair_post}\n{i+1} & {repair_syn} & {repair_sat}\n"
        repairs += "\n"
    print(repairs)

def rq3(data):
    data = data[data["aggregation_strategy"] == "no_aggregation"]
    for dimension in ["111", "011", "101", "110"]:
        dim_data = data[data["config_id"].str.endswith(dimension)]
        runs_data = dim_data.groupby(["config_id", "sample_id"]).agg(min=("f_correctness", "min"))
        runs = round(len(runs_data[runs_data["min"].apply(is_zero)]) / len(runs_data), 2)
        rate_data = dim_data[dim_data["f_correctness"].apply(is_zero)]
        rate = round(len(rate_data) / len(dim_data), 2)
        sem = (round(rate_data["f_des_semantic"].mean(), 2), round(rate_data["f_des_semantic"].median(), 2))
        syn = (round(rate_data["f_des_syntactic"].mean(), 2), round(rate_data["f_des_syntactic"].median(), 2))
        sat = (round(rate_data["f_des_satisfaction"].mean(), 2), round(rate_data["f_des_satisfaction"].median(), 2))
        print(f"{dimension} & {rate} & {sem[0]},{sem[1]} & {syn[0]},{syn[1]} & {sat[0]},{sat[1]} \\\\")

if __name__ == "__main__":
    data = pd.read_csv("output/results.csv")
    case_studies = {"AFC": ["AFC29", "AFC33"], "AT": ["AT1", "AT2"], "CC": ["CC1", "CCX"], "EU": ["EU3"],
                    "NNP": ["NNP3a", "NNP3b", "NNP4"], "TUI": ["TU1", "TU2"]}
    rq2(case_studies, data)
    rq3(data)

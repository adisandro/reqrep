#!/usr/bin/env python3
import math

import pandas as pd

def is_zero(x):
    return math.isclose(x, 0.0, abs_tol=1e-6)

def rq2_useful(sorted_data):
    first_useful = None
    syn_of_first_useful = None
    sat_of_first_useful = None
    num_useful = 0
    for i in range(10):
        repair = sorted_data.iloc[i]
        repair_req = repair["config_id"].split("_")[1]
        repair_pre = repair["precondition"].replace("_", "\\_")
        repair_post = repair["postcondition"].replace("_", "\\_")
        repair_syn = round(repair["f_des_syntactic"], 2)
        repair_sat = round(repair["f_des_satisfaction"], 2)
        print(f"\n{repair_req}: {repair_pre} => {repair_post}\n")
        useful = input("Useful? ")
        if useful == "y":
            num_useful += 1
            if first_useful is None:
                first_useful = i+1
                syn_of_first_useful = repair_syn
                sat_of_first_useful = repair_sat
    return first_useful, syn_of_first_useful, sat_of_first_useful, num_useful


def rq2(case_studies, data):
    data = data[(data["aggregation_strategy"] == "no_aggregation") & (data["config"] == "hp_increase_num_offsprings") &
                data["config_id"].str.contains("111")]
    correct_data = data[(data["f_correctness"].apply(is_zero)) & (data["f_des_semantic"].apply(is_zero))]
    results = ""
    for case_study in case_studies:
        case_data = data[data["config_id"].str.startswith(case_study)]
        case_correct_data = correct_data[correct_data["config_id"].str.startswith(case_study)]
        ratio = round(len(case_correct_data)/len(case_data), 2)
        print("\n--SYN--\n")
        sorted_data_syn = case_correct_data.sort_values(by=["f_des_syntactic", "f_des_satisfaction"])
        first_useful_syn, syn_of_first_useful_syn, sat_of_first_useful_syn, num_useful_syn = rq2_useful(sorted_data_syn)
        print("\n--SAT--\n")
        sorted_data_sat = case_correct_data.sort_values(by=["f_des_satisfaction", "f_des_syntactic"])
        first_useful_sat, syn_of_first_useful_sat, sat_of_first_useful_sat, num_useful_sat = rq2_useful(sorted_data_sat)
        results += f"{case_study} & {ratio} & {first_useful_syn} & {first_useful_sat} & {syn_of_first_useful_syn} & "\
                   f"{syn_of_first_useful_sat} & {sat_of_first_useful_syn} & {sat_of_first_useful_sat} & "\
                   f"{num_useful_syn}/10 & {num_useful_sat}/10 \\\\\n"
    print(results)

def rq3(data):
    data = data[data["aggregation_strategy"] == "no_aggregation"]
    for dimension in ["111", "011", "101", "110"]:
        dim_data = data[data["config_id"].str.contains(dimension)]
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

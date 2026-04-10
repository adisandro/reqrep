# ReqRep - A framework for CPS requirements repair

This [repository](https://doi.org/10.5281/zenodo.19488528) contains the software and artifacts associated to the paper "*Automated Repair of Requirements for Cyber-Physical Systems in Simulink Requirements Tables*" by Aren A. Babikian, Alessio Di Sandro, Federico Formica, Claudio Menghi, and Marsha Chechik, presented at FSE 2026.  
This document provides instructions on how to use the tool and replicate the results presented in the paper.

For information on the software requirements to run the tool, see [REQUIREMENTS.md](REQUIREMENTS.md).  
For a step-by-step guide on how to install the tool, see [INSTALL.md](INSTALL.md).  
For licensing information, see [LICENSE.txt](LICENSE.txt).

## Overview

ReqRep is a Python tool to repair test requirements for Cyber-Physical Systems (CPS).
It restores compliance between system behavior (as captured by trace suites) and formalized requirements, based on repair desirability metrics.

To verify the correct installation, run the following from the command line:

```bash
python3 bin/main.py data/traces REQ
```

This should require less than a minute to complete, and will create a folder called `output/traces_REQ_noaggregation_111_default`, containing the results of a single iteration of the tool.
 
## General Usage

Running the repair tool from the command line requires you to specify the trace suite directory and the requirement name. Optional arguments allow you to customize the repair process.

```bash
python3 bin/main.py [-h] [-p PREV0] [-i ITERATIONS] [-n NUMBERS] [-a AGGREGATION] [-w WEIGHTS] [-ac APPROACH_CONFIG] [-s SUFFIX] [-v] [-o OUTPUT_DIR] trace_suite requirement
```

### Mandatory arguments

- `trace_suite`: Path to the directory containing the trace suite (CSV files)
- `requirement`: The name of the requirement to check

### Optional arguments

- `-h`, `--help`: Show this help message and exit
- `-p`, `--prev0` `PREV0`: Initial value for the prev() operator at time 0 (defaults to 0.0)
- `-i`, `--iterations` `ITERATIONS`: The number of iterations the approach tries when repairing, defaults to 10
- `-n`, `--numbers` `NUMBERS`: When generating numbers, each variable has a window [min, max] based on the values seen in the traces; this widens/shrinks the window by a factor, defaults to 1.2
- `-a`, `--aggregation` `AGGREGATION`: The aggregation strategy in {no_aggregation, weighted_sum}, defaults to no_aggregation
- `-w`, `--weights` `WEIGHTS`: The desirability weights, defaults to 1.0,1.0,1.0
- `-ac`, `--approach-config` `APPROACH_CONFIG`: Category of hyperparameters to use (see [src/repair/approach/approachConfig.py](src/repair/approach/approachConfig.py))
- `-s`, `--suffix` `SUFFIX`: An optional output file suffix
- `-v`, `--verbose`: Activates logging
- `-o`, `--output_dir` `OUTPUT_DIR`: Directory to save outputs, defaults to 'output'

### Pre-encoded trace suites and requirements

Trace suites and requirements are pre-encoded in the file [bin/utils.py](bin/utils.py). The tool can be invoked with the following variants:

```bash
python3 bin/main.py data/dummy REQ
python3 bin/main.py data/traces REQ
python3 bin/main.py data/case_studies/AFC AFC29
python3 bin/main.py data/case_studies/AFC AFC33
python3 bin/main.py data/case_studies/AT AT1
python3 bin/main.py data/case_studies/AT AT2
python3 bin/main.py data/case_studies/CC CC1
python3 bin/main.py data/case_studies/CC CCX
python3 bin/main.py data/case_studies/EU EU3
python3 bin/main.py data/case_studies/NNP NNP3a
python3 bin/main.py data/case_studies/NNP NNP3b
python3 bin/main.py data/case_studies/NNP NNP4
python3 bin/main.py data/case_studies/TUI TU1
python3 bin/main.py data/case_studies/TUI TU2
```

## Evaluation replication

This section explains how to replicate the experiments described in Section 6 (Evaluation) of the corresponding paper.

### RQ1

For a **complete** replication of the evaluation, for all six models (*AFC, AT, CC, EU, NN, TUI*) and all the seven tool configurations (*V1 to V7*), run the command below.

```bash
python3 bin/evaluation.py
python3 bin/evaluation.py -p 4 # Will use 4 parallel processes
```

Results are saved in the `output` folder (the original paper results are in the `output_paper` folder).
Please note that you can specify the number of parallel processes you wish to run using the `-p` or `--process` flag, or otherwise default to the number of processors on your computer.  
The complete evaluation is time-consuming and takes hours to execute, depending on the hardware.

[*Note: Currently V2 and V4 (the configurations without z3) are not executed.*]

For a **partial** replication of the Evaluation, the user can specify which configurations they are interested in as an additional argument.
The configuration codes are `V1` to `V7` for the seven tool configurations, and `Abl1`, `Abl2`, and `Abl3` for the three special configurations used in RQ3 (the ablation study).

```bash
python3 bin/evaluation.py V6 V7 Abl1 # Will replicate only V6, V7, and Abl1.
python3 bin/evaluation.py V1         # Will replicate only V1.
```

For each requirement and tool configuration, the tool will create a dedicated folder inside the folder `output`. These folders have the following naming scheme:  
[Model Name]\_[Requirement Name]\_[Aggregation Strategy]\_[Weights]\_[Additional specifiers]  
For example, `NNP_NNP3a_noaggregation_111_hp_increase_num_offsprings` indicates that this folder contains the results for the requirement NNP3a of the model NNP, when analyzed by the tool with aggregation strategy "No Aggregation", desirability weights of 1, 1, and 1, and doubling the number of offspring (i.e., tool configuration V7).
This folder contains a .txt file for each run of the experiment (10 by default). The .txt file contains all the repaired requirements generated in that run and their correctness and desirability scores.

In addition to this, the evaluation script also creates a `results.csv` file in `output`, which summarises the results for all the models and tool configurations analysed.
Here is an example of the expected folder structure:

```
root/
├── output/
│   ├── NNP_NNP3a_noaggregation_111_hp_increase_num_offsprings/
│   │   ├── repair0.txt
│   │   ├── repair1.txt
│   │   ├── ...            # Results for all the iterations between 0 and 9
│   │   └── repair9.txt
│   ├── ...                # Results for other models and requirements
│   └── results.csv
└── ...                    # Other folders and files
```

To help with the analysis of the results, we share a Matlab script: `plotBoxplot.m`.
This script generates a set of summary tables that contain all the numbers mentioned in Section 6.3, as well as the boxplots in Figure 7. Please note that if you replicate the experiments (using `bin/main.py` or `bin/evaluation.py`), **the results may be slightly different from the ones presented in the paper, due to stochastic fluctuations**.  
This script can be run from the Matlab IDE using any directory as the current active directory, as long as the script `scripts/ScriptsRQ1/plotBoxplot.m` is on the active path.  
The script will produce the two boxplot figures inside the folder `Figures` and three .csv files summarizing for each model and each configuration, respectively, the Satisfaction Extent score (`Table_Satis.csv`), the Syntactic Similarity score (`Table_Synt.csv`), and the number of repaired requirements (`repairNumber.csv`).
The `ScriptsRQ1` folder will have the following structure:

```
root/
├── scripts/
│   ├── ScriptsRQ1/
│   │   ├── Figures/
│   │   │   ├── Boxplot_Satis.pdf  # Should match Figure 7.a in the paper
│   │   │   ├── Boxplot_Synt.pdf   # Should match Figure 7.a in the paper
│   │   │   └── Repairs.pdf        # Figure not used in the paper
│   │   ├── plotBoxplot.m
│   │   ├── repairNumber.csv
│   │   ├── Table_Satis.csv
│   │   └── Table_Synt.csv
│   └── ...                        # Other scripts
└── ...                            # Other folders and files
```

**Note:** Please note that if you change the name or generate new results file, you will need to update the script (see Lines 31-37).

```matlab
31: fileList(1).Folder = "output";
32: fileList(1).FileName = "results.csv";
33: fileList(1).Aggregation = "no_aggregation";
34: fileList(1).Config = "default";
35: fileList(1).Weights = "[1.0, 1.0, 1.0]";
36: fileList(1).TautologyZ3 = true;
37: fileList(1).Label = "V1";
```

* `Folder`: Path from the root folder to the folder containing the results file.
* `FileName`: Name of the results file. A single file may contain the results for several tool configurations.
* `Aggregation`, `Config`, `Weights`, `TautologyZ3`: Properties of the chosen tool configuration. They will be used to filter the results file.
* `Label`: Label assigned to the tool configuration. It will be used in the generated figures and tables.

### RQ2/RQ3

This requires the **complete** execution of RQ1. Alternatively, you can reuse the paper results by renaming the folder `output_paper` to `output`.

Run the following command to generate Tables 4 and 5.

```bash
python3 scripts/rq2rq3.py
yes | python3 scripts/rq2rq3.py # answers y to all prompts
```

## Extending the evaluation

### Change tool configuration

Several elements of the tool can be modified and personalized.
By using the additional arguments of `main.py`, it is possible to test combinations of tool configuration options that were not explored in the original paper (see the [General Usage](#general-usage) section).
For example, the following tool configuration has not been previously considered:

```bash
python3 bin/main.py data/traces REQ --aggregation weighted_sum --weights 3.0,2.0,5.0 --numbers 1.4
```

In addition, it is also possible to define new desirability metrics by modifying `main.py` and choosing among the different implementations (or creating new implementations) for:

- *Semantic Integrity*: [src/repair/fitness/desirability/semanticintegrity.py](src/repair/fitness/desirability/semanticintegrity.py)
- *Syntactic Similarity*: [src/repair/fitness/desirability/syntacticsimilarity.py](src/repair/fitness/desirability/syntacticsimilarity.py)
- *Satisfaction Extent*: [src/repair/fitness/desirability/satisfactionextent.py](src/repair/fitness/desirability/satisfactionextent.py)

### Define a new requirement under analysis

If you want to add a new requirement to one of the existing models, you need to modify `bin/utils.py`.
This file contains the set of variables and the original requirement formulation for all models.
Make sure that the variable names match the ones used in the trace files.  
The file currently contains several examples, showing the correct syntax to:

- Define pre- and post-conditions: `"[Req. label]": ("[Pre-condition]","[Post-condition]")`
- Use boolean operators: `and(...,...)` and `or(...,...)`).
- Use relational operators: `lt(...,...)`, `gt(...,...)`, `le(...,...)`, `ge(...,...)`, and `eq(...,...)`

### Define a new model under analysis

Applying the tool on a new model requires (i) the definition of the new set of requirements for the model (see the section above) and (ii) the definition of the new trace suite.

To define a new trace suite, you need to save each trace as an individual .csv file using the model label as part of the name.
Within the model, the data must be organized considering each row to be a timestep and each column to be a signal.
No distinction is made between input and output signals at this stage.  
The first row of the file is reserved for the header, which defines the signal names and specifies the units of measurement using the following syntax: `[Signal name]|[Units of measurement]`.
The unit of measurement can be any 1 word string and will be used to compute the Semantic Integrity score, to check that the signals being compared have the same unit of measurement.
Here is an example of the required structure for a trace file:

```csv
Time|s,Speed|kph,Distance|m,MotorTorque|Nm
0.0,30.0,0.0,5.2
0.1,30.2,8.3,5.0
0.2,30.4,16.7,5.4
...
```

## Citation

The paper associated with this Artifact can be cited as follows:

```latex
@article{Babikian_2026_Automated,
 author = {Babikian, Aren A. and Di Sandro, Alessio and Formica, Federico and Menghi, Claudio and Chechik, Marsha},
 title = {Automated Repair of Requirements for Cyber-Physical Systems in Simulink Requirements Tables},
 year = {2026},
 issue_date = {July 2026},
 publisher = {Association for Computing Machinery},
 address = {New York, NY, USA},
 volume = {XXX},
 url = {https://doi.org/XXX},
 doi = {XXX},
 journal = {XXX},
 articleno = {XXX},
 numpages = {24},
 series = {FSE}
}
```

This Artifact can be cited as follows:

```latex
@misc{Artifact_Babikian_2026_Automated,
 author = {Babikian, Aren A. and Di Sandro, Alessio and Formica, Federico and Menghi, Claudio and Chechik, Marsha},
 title = {Replication package for Automated Repair of Requirements for Cyber-Physical Systems in Simulink Requirements Tables},
 year = {2026},
 month = {April},
 publisher = {Zenodo},
 doi = {10.5281/zenodo.19488528},
 url = {https://doi.org/10.5281/zenodo.19488528},
}
```

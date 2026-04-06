# Artifact documentation

This repository contains the Artifact associated to the paper "*Automated Repair of Requirements for Cyber-Physical Systems in Simulink Requirements Tables*" by Aren A. Babikian, Alessio Di Sandro, Federico Formica, Claudio Menghi, and Marsha Chechik, presented at FSE 2026.  
This document provides instructions on how to replicate the results presented in the paper and reuse the tool for additional experiments.

## Statement on Artifact Availability [move to `STATUS.txt`]

This Artifact is **available**: it is contained on a persistent repository (Zenodo), it is publicly available, and it has been assigned a DOI.

## Statement on Artifact Functionality [move to `STATUS.txt`]

This Artifact is **functional**: it contains detailed instructions on how to install the tool (see `INSTALL.txt`) and how to replicate all the results presented in the Evaluation section of the associated paper (see the "*Experiments replication*" section in `README.md`).

The complete replication of all the results in the paper is very time-consuming and requires approx 12 hours to generate all the results. We suggest that the reviewers replicate only the results for the tool configuration V1. This would require only 2 hours (with no parallelization).  
This can be achieved by using the following command after installing the tool:

```bash
python bin/evaluation.py V1
```

[*Note from Federico: Should we provide the reviewers an even faster partial replication of the results? Maybe only V1 and only for AT (approx. time: 5 mins).*]

## Statement on Artifact Reusability [move to `STATUS.txt`]

This Artifact is **reusable**: it contains detailed instructions on how to apply the tool using different configuration parameters (see the "*Change tool configuration*" section in `README.md`) and different models and trace suites (see the "*Change Model under Analysis*" section in `README.md`).

## Installation guide

For information on the software and hardware requirements to run the tool, see `REQUIREMENTS.txt`.  
For a step-by-step guide on how to install the tool, see `INSTALL.txt`.

To verify the correct installation, try to run the following command within the virtual environment created in Step 2 of the installation process.

```bash
python bin/main.py data/traces REQ
```

This should require less than a minute to complete, and it should create a folder called `traces_REQ_noaggregation_111_default` inside `output`, containing the results for a single iteration of the tool.

## Artifact Requirements [move to `REQUIREMENTS.txt`]

Running the tool has the following requirements:

- Python 3.12 or higher.
- pip (Python package installer)

The Installation process will download and install all the required Python packages using pip. 
[*Note from Federico: I increased the Python required version from 3.6 to 3.12. Older Python versions (3.6 to 3.11) will break due to the different handling of f-strings.*]

The Artifact also contains a Matlab script (`scripts\ScriptsRQ1\plotBoxplot.m`) that produces the boxplots in Figures 7.a and 7.b of the corresponding paper and produces a summary of the results.
This is not a fundamental part of the tool since it only performs some basic data analysis on the results produced by the tool.
To run this script, there is one additional requirement:

- Matlab 2025a or higher.

## Artifact Installation [move to `INSTALLATION.txt`]

[*Note from Federico: Change this process if we decide to use a Docker image.*]

The Installation process requires only 3 steps:

1. Download the Artifact from Zenodo and unzip the folder:
 
   ```bash
   cd [Path/to/downloaded/folder]
   unzip ReplicabilityPackage.zip
   cd ReplicabilityPackage
   ```

2. (*Recommended*) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package and the required dependencies:
 
   ```bash
   pip install -e .
   ```
   [*Note from Federico: When I installed it, the package did not contain z3 as a dependency and I had to install it manually.*]
   
## General Usage

After installing the package, you can run the repair tool from the command line. The script requires you to specify the trace suite directory and one or more input variable names. Optional arguments allow you to customize the repair process.

[*Note from Federico: Why do we need to specify the name of the input vars? Is it not enough to give the trace suite?*]

#### Usage

```bash
python bin/main.py [-h] [-p PREV0] [-t THRESHOLD] [-i ITERATIONS] trace_suite input_vars [input_vars ...]
```

- `trace_suite`: Path to the directory containing the trace suite (CSV files)
- `input_vars`: One or more input variable names (space-separated)

#### Optional arguments:

[*Note from Federico: I think this part should be updated. There are many more optional arguments that we can use.*]

- `-h`, `--help`: Show help message and exit
- `-p PREV0`, `--prev0 PREV0`: Value to use for the previous time step when evaluated at time step 0 (default: 0)
- `-t THRESHOLD`, `--threshold THRESHOLD`: Threshold value for repair (default: 100.0)
- `-i ITERATIONS`, `--iterations ITERATIONS`: Number of repair iterations (default: 10)

#### Example

```bash
python bin/main.py data/traces xin reset TL BL dT ic yout
```

This will process all trace files in the `data/traces/` directory using the specified input variables.

#### Notes

- All arguments after the trace suite directory are treated as input variable names.
- Use the `-h` flag to see all available options and their descriptions.
- Make sure your Python environment has all dependencies installed (see Installation section).

<!-- ### Input Format

Each CSV file in the trace suite should have columns like:
 TODO -->

## Experiments replication

This section explains how to replicate the experiments described in Section 6 (Evaluation) of the corresponding paper.

### RQ1

For a **complete** replication of the Evaluation, for all six models (*AFC, AT, CC, EU, NN, TUI*) and all the seven tool configurations (*V1 to V7*), run the command below.  
This script will automatically save the results in the `output` folder.
Please note that you can specify the number of parallel processes you wish to execute using the `-p` or `--process` flag.

[*Note: Currently `evaluation.py` does not execute V2 and V4 (the configurations without z3).*]

```bash
python bin/evaluation.py
python bin/evaluation.py -p 4 # Will open 4 parallel processes
```

For a **partial** replication of the Evaluation, the user can specify which configurations they are interested in as an additional argument.
The configuration codes are `V1` to `V7` for the seven tool configurations, and `Abl1`, `Abl2`, and `Abl3` for the three special configurations used in RQ3 (the ablation study).

```bash
python bin/evaluation.py V2 V4 Abl1 # Will replicate only V2, V4, and Abl1.
python bin/evaluation.py V1 -p 2    # Will replicate only V1 using 2 parallel processes.
```

For each requirement and tool configuration, the tool will create a dedicated folder inside the folder `output`. These folders have the following naming scheme:  
[Model Name]\_[Requirement Name]\_[Aggregation Strategy]\_[Weights]\_[Additional specifiers]  
For example, `NNP_NNP3a_noaggregation_111_hp_increase_num_offsprings` indicates that this folder contains the results for the requirement NNP3a of the model NNP, when analyzed by the tool with aggregation strategy "No Aggregation", desirability weights of 1, 1, and 1, and doubling the number of offspring (i.e., tool configuration V7). 
Note that the weights are rounded to the nearest integer when creating the name of the folder.  
This folder contains a .txt file for each run of the experiment (10 by default). The .txt file contains all the repaired requirements generated in that run and their correctness and desirability scores.

In addition to this, the `evaluation.py` script also creates a `results.csv` file in `output`, which summarises the results for all the models and tool configurations analysed.
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
32: fileList(1).FileName = "results_V1_V3.csv";
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

### RQ2

### RQ3

## Extending the evaluation

### Change tool configuration

Several elements of the tool can be modified and personalised.
By using the additional arguments of `main.py`, it is possible to test combinations of tool configuration options that were not explored in the original paper (see the [General Usage](##general-usage) section).
For example, the following tool configuration has not been previously considered:

```bash
python bin/main.py --aggregation weighted_sum --weights 3.0,2.0,5.0 data/traces xin reset TL BL dT ic yout
```

In addition, it is also possible to define new values for the tool configuration parameters:

- *Create a new Aggregation Strategy*:
- *Create a new set of Weights*: A new set of weights can be defined simply using the optional arguments of `main.py`. The field `-w` or `--weights` allow to define a list of any three floats separated by a comma (no spaces in the middle) as the weights of the desirability metric. Please note that the weights refer in order to Semantic Integrity, Syntactic Similarity, and Satisfaction Extent.
- *Create a new Search-Approach*:
- *Create a new Semantic Integrity checker*:
- *Create a new Desirability metric*:

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
 doi = {XXX},
 url = {https://doi.org/XXX},
}
```
# Artifact documentation

This repository contains the Artifact associated to the paper "*Automated Repair of Requirements for Cyber-Physical Systems in Simulink Requirements Tables*" by Aren A. Babikian, Alessio Di Sandro, Federico Formica, Claudio Menghi, and Marsha Chechik, presented at FSE 2026.  
This document contains information on how to replicate the results presented in the paper and reuse the tool for additional experiments.

## Statement on Artifact Availability [move to `STATUS.txt`]

This Artifact is **available**: it is contained on a persistent repository (Zenodo), it is publicly available, and it has been assigned a DOI.

## Statement on Artifact Functionality [move to `STATUS.txt`]

This Artifact is **functional**: it contains detailed instructions on how to install the tool (see `INSTALL.txt`) and how to replicate all the results presented in the Evaluation section of the associated paper (see the "*Experiments replication*" section in `README.md`).

The complete replication of all the results in the paper is very time-consuming and requires approx. 12 hours to generate all the results. We suggest the reviewers to replicate only the results for the tool configuration V1.

[*Note: Should we add an option to `evaluation.py` to run only the experiments for V1?*]

## Statement on Artifact Reusability [move to `STATUS.txt`]

This Artifact is **reusable**: it contains detailed instructions on how to apply the tool using different configuration parameters (see the "*Change tool configuration*" section in `README.md`) and different models and trace suites (see the "*Change Model under Analysis*" section in `README.md`).

## Installation guide

For information on the software and hardware requirements to run the tool, see `REQUIREMENTS.txt`.  
For a step-by-step guide in how to install the tool, see `INSTALL.txt`.

## Artifact Requirements [move to `REQUIREMENTS.txt`]

Running the tool has the following requirements:

- Python 3.12 or higher.
- pip (Python package installer)

The Installation process will download and install all the required Python packages using pip. 
[*Note from Federico: I increased the Python required version from 3.6 to 3.12. Older Python versions (3.6 to 3.11) will break due to the different handling of f-strings.*]

The Artifact also contains a Matlab script (`scripts\ScriptsRQ1\plotBoxplot.m`) that produces the boxplots in Figures 7.a and 7.b of the corresponding paper and produces a summary of the results.
This is not a fundamental part of the tool since it only performs some basic data analysis on the results produced by the tool.
To run also this script, there is one additional requirement:

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

This sections explains how to replicate the experiments described in Section 6 (Evaluation) of the corresponding paper.

### RQ1

To reproduce all the results in the Evaluation, for all six models (*AFC, AT, CC, EU, NN, TUI*) and all the seven tool configurations (*V1 to V7*), run the following command.
This script will automatically save the results in the `output` folder.

```
python bin/evaluation.py
```

[*ToDo: Add details on how to interpret the results.*]

### RQ2

### RQ3

## Extending the evaluation

### Change tool configuration

### Change Model under Analysis

## Citation

The paper associated to this paper can be cited as follows:

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
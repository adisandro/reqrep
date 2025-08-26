# ReqRep - A framework for CPS requirements repair

A Python tool for repairing test requirements based on trace suites and repair desirability metrics.

## Overview

ReqRep repairs requirements for Cyber-Physical Systems (CPS) to restore compliance between system behavior (as captured by trace suites) and formalized requirements.

**Inputs:**
- **Trace suite directory:** A folder containing `.csv` files, each representing signal values over time for the CPS-under-test.
- **Requirement:** A Simulink Requirements Table logic expression that may not be satisfied by the traces.
- **Desirable property:** A property to optimize during repair.

**Output:**  
A repaired requirement that:
- (1) Satisfies all traces in the suite,
- (2) Optimizes for the desirable property.

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Install from Source

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd reqrep
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```
   Or:
   ```bash
   pip install .
   ```

## Usage

### Command Line Usage

After installing the package, you can run the repair tool from the command line. The script requires you to specify the trace suite directory and one or more input variable names. Optional arguments allow you to customize the repair process.

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

## Project Structure

```
reqrep/
├── bin/
│   └── main.py                  # Main entry point
├── data/
│   ├── case_studies/            # Case study data (AFC, AT-AT1, ...)
│   ├── dummy/                   # Dummy trace data
│   └── traces/                  # Example traces
├── scripts/                     # Miscellaneous scripts
├── src/
│   └── repair/
│       ├── approach/
│       │   ├── optimization/    # Approach based on genetic programming
│       │   └── transformation/  # Transformation-based approach
│       ├── fitness/             # Fitness metrics (correctness, desirability)
│       └── grammar/             # Requirement Grammar
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

<!-- ## Development

### Running from Source

If not installed, run directly:

```bash
cd reqrep
python -m bin.main <path-to-trace-suite>
```

### Available Case Studies

Case studies are in `case_studies/case_studies/`:

- `AFC/` - Abstract Fuel Control (100 traces)
- `AT/` - AT test cases
- `CC/` - CC test cases
- `EU/` - EU test cases
- `NNP/` - NNP test cases
- `TUI/` - TUI test cases

## Requirements

Example requirements:
- `BL <= ic <= TL and reset == 0` → `yout == ic`
- `True` → `TL >= yout >= BL`

## Transformations

Supported transformations include:
- **Add true:** Adds `True or (...)` to preconditions and postconditions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is open source. See the project files for details. -->

<!-- ## Contact

- **Author:** Alessio Di Sandro
- **Email:** alessio.disandro@gmail.com -->

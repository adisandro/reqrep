# Installation Requirements

## Docker

The tool can run within a Docker environment.
Follow the instructions on the [Docker website](https://docs.docker.com/desktop) to install it.

## Native

Running the tool natively has the following requirements:

- Python 3.12 or higher.
- pip (Python package installer)

The Installation process will download and install all the required Python packages using pip. 

The Artifact also contains a Matlab script (`scripts\ScriptsRQ1\plotBoxplot.m`) that produces the boxplots in Figures 7.a and 7.b of the corresponding paper and produces a summary of the results.
This is not a fundamental part of the tool since it only performs some basic data analysis on the results produced by the tool.
To run this script, there is one additional requirement:

- Matlab 2025a or higher.
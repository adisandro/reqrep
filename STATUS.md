# Artifact Evaluation

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

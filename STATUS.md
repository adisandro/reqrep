# Artifact Evaluation

## Statement on Artifact Availability

This Artifact is **available**: it is available in a persistent repository on Zenodo, it is publicly available, and it has been assigned a DOI (https://doi.org/10.5281/zenodo.19488528).

## Statement on Artifact Functionality

This Artifact is **functional**: it contains detailed instructions on how to install the tool (see `REQUIREMENTS.md` and `INSTALL.md`) and how to replicate all the results presented in the Evaluation section of the associated paper (see the "*Evaluation replication*" section in `README.md`).

The complete replication of all the results in the paper is time-consuming and requires hours to generate all the results, depending on the hardware. We suggest that the reviewers replicate only the results for the tool configuration V1. This would require only 2 hours.  
This can be achieved by using the following command after installing the tool:

```bash
python3 bin/evaluation.py V1
```

## Statement on Artifact Reusability

This Artifact is **reusable**: it contains detailed instructions on how to apply the tool using different configuration parameters (see the "*Change tool configuration*" section in `README.md`) and different models and trace suites (see the "*Change Model under Analysis*" section in `README.md`).

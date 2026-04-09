# Installation Instructions

## Docker

1. Download the paper replicability package from [Zenodo](https://doi.org/10.5281/zenodo.19488528) and unzip it:
 
   ```bash
   cd [path/to/downloaded/folder]
   unzip ReplicabilityPackage.zip
   cd ReplicabilityPackage
   ```

2. Load the Docker image:

   ```bash
   TODO
   ```

## From Source

1. Download the paper replicability package from [Zenodo](https://doi.org/10.5281/zenodo.19488528) and unzip it:
 
   ```bash
   cd [path/to/downloaded/folder]
   unzip ReplicabilityPackage.zip
   cd ReplicabilityPackage
   ```

2. (*Recommended*) Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package and the required dependencies:
 
   ```bash
   python3 -m pip install -e .
   ```

### Tool-only

If you just want to try the tool rather than the paper replicability package, replace step 1 with the following:

```bash
git clone https://github.com/adisandro/reqrep
cd reqrep
```

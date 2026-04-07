# Installation Instructions

## Docker

A Docker image pre-loaded with our tool is available [here](TODO).
Install it with the following steps:

```bash
TODO
```

## From Source

The Installation process requires 3 steps:

1. Download the paper replicability package from [Zenodo](TODO) and unzip it:
 
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

If you just want to try the tool rather than the replicability package, you can replace step 1 with the following:

```bash
git clone <repository-url>
cd reqrep
```

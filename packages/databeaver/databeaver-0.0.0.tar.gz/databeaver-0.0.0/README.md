# Data Beaver - Data Model Orchestration
Data Beaver is a tool that allows teams to easily realize, test, version, and share their data models. 

## Overview
The aim of data beaver is to create a deterministic process for realizing a given data model. 
 

## Major Releases
| Version | Goal |
|---------|--------------------------------|
|0.1.0    | Build a Model against Postgres |
## How To

### Install Data Beaver
To install Data Beaver you can run the command below.
```bash
pip install databeaver
```

### Execute a model 
Data Beaver can be used as either a command line application or as a module for a more direct integration. 
#### Module Usage
```python
from databeaver import DataModel
model = DataModel()
model.build()
```

#### Command Line Usage
```bash
```

This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
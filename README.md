# Juniter

This tool was built to serve as an evaluation tool for an **OOP** University-level course.

It uses a maven template project and the maven command-line tool through python to run tests on multiple projects and outputs the results to CSV files.

**Juniter supports both Junit 4 and 5.**

The tool was intended to be used to evaluate "vanilla" java projects built without the use of any package-manager, so it won't work with gradle nor ant, but it can be repurposed to evaluate maven projects by changing the template project. 

# Dependencies

## python

version: python 3.10.x

```shell
cd path/tp/Juniter
python3 -m pip install -r requirements.txt
```

## java


version: openjdk 17.0.6 2023-01-17

## mvn

version: Apache Maven >=3.6.3


# Usage

## Command-Line Interface

```shell
usage: juniter-cli.py [-h] [-m M] [-o O] P T

Process plain java projects with junit tests.

positional arguments:
  P                  path to the projects' compressed file
  T                  path to the tests' compressed file

options:
  -h, --help         show this help message and exit
  -m M, --mapping M  path to the mapping file
  -o O, --output O   path to the output directory
```

inside the compressed projects file each project should be also compressed (.rar, .zip)
```
└── projects.zip
    ├── team1.zip
    ├── team-02.zip
    ├── Team 3.zip
    └── Team_4.zip
```

while the compressed tests file should contain .java files.

```
└── tests.zip
    ├── Test1.java
    └── Batch3TestFile.java
```

The mapping file should be a CSV file with 2 columns, which can be optionally provided to alias one or more project's file name in the output.

| From | To |
|---|---|
|team1.zip|Team 1|
|team 3.zip|Team 3|



## Streamlit Interface

Running through Streamlit locally:

```shell
cd path/to/Juniter
streamlit run StreamLit/Home.py
```

or simply visit the [streamlit web interface](https://juniter.streamlit.app/)
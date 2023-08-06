
Package for Multi-Criteria Decision Analysis named `mcda` (**Alpha**).


# Table of contents

[TOC]


# Package description

This package is used as a basis to represent MCDA problems as well as solve them.
It currently contains functionalities to accurately describe a MCDA problem.
It also contains relatively low-level plotting functions to visualize a MCDA problem and its solution.
The repository also contains [jupyter notebooks](https://jupyter.org/) that can be used as tutorials.

It is hosted on PyPI: [mcda](https://pypi.org/project/mcda/)

# Install

The only non-python requirement is: graphviz
It can be installed using the following command (for Debian/Ubuntu):
```bash
sudo apt-get install graphviz
```

Package can then be installed using simply pip: `pip install mcda`

It can also be installed by cloning this git, then following the instructions grouped [here](INSTALL.md) to install the package in editable mode or install its requirements for development.


# Documentation

Documentation on this package can be found [here](https://py-mcda.readthedocs.io/).

It also can be built locally by executing the following command in the package root folder:

```bash
make doc
```

and then visiting `doc/html/index.html` (this can be useful if you're not using a released version of this package).


# Notebooks

We added [jupyter notebooks](https://jupyter.org/) that can be run as examples in [examples/](examples/).


# Developers' corner

This package is [PEP8](https://www.python.org/dev/peps/pep-0008/) compliant with a maximum line length of **79**, and is statically typed using [type hints](https://docs.python.org/3/library/typing.html).

Documentation, unit tests and example notebooks **shall be** developed alongside the package features.

A suite of linters must be set up in order to enforce those guidelines, you can use the [Makefile](Makefile) to see their parameters and options:

* [flake8](https://flake8.pycqa.org/en/latest/)
* [isort](https://pycqa.github.io/isort/)
* [black](https://pypi.org/project/black/)
* [mypy](https://mypy.readthedocs.io/en/stable/)

Changes **should not** be commited if the linters don't validate the changes and the unit tests don't run.

For more details, read the [guideline](CONTRIBUTING.md).


# Known issues

None

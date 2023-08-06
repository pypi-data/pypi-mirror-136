<!--
This file is part of CoVeriTeam,
a tool for on-demand composition of cooperative verification systems:
https://gitlab.com/sosy-lab/software/coveriteam

SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

# CoVeriTeam

## A Tool for On-Demand Composition of Cooperative Verification Systems

[![Apache 2.0 License](https://img.shields.io/badge/license-Apache--2-brightgreen.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![PyPI version](https://img.shields.io/pypi/v/CoVeriTeam.svg)](https://pypi.python.org/pypi/CoVeriTeam)
[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.3818283.svg)](https://doi.org/10.5281/zenodo.3818283)
[![CI](https://gitlab.com/sosy-lab/software/coveriteam/badges/main/pipeline.svg)](https://gitlab.com/sosy-lab/software/coveriteam/pipelines)

CoVeriTeam consists of a language for on-the-fly composition
of cooperative verification tools from existing components; and its execution engine.
The concept is based on
verification artifacts (programs, specifications, witnesses, results) as basic objects,
verification actors (verifiers, validators, testers, transformers) as basic operations, and
defines composition operators that make it possible to easily describe new compositions,
taking verification artifacts as interface between the verification actors.

## Directory Structure of this repository
The CoVeriTeam directory is structured as follows:
```
    .
    |-- actors/                    # YAML actor-definition files for atomic actors
    |-- bin/                       # script to execute CoVeriTeam    
    |-- contrib/                   # script to create an independent archive packaging all dependencies
    |-- coveriteam/                # Python source code
        |-- actors/                # atomic actors like ProgramVerifier, ProgramTester, etc.
        |-- interpreter/           # interpreter for the CoVeriTeam language
        |-- language/              # core concepts of the CoVeriTeam language: actors, artifacts, composition
        |-- parser/                # grammar and generated parser
    |-- doc/                       # documentation
    |-- examples/                  # tutorial examples and applications; more information in examples/README.md
    |-- utils/                     # external libraries required for development    
    |-- smoke_test_all_tools.sh    # report tool information from all atomic actors in the actors/ folder
    |-- LICENSE                    # Apache 2.0 license file
    |-- LICENSES                   # collection of licenses for artifacts in this repository
```

## Installation
CoVeriTeam can be installed from [PyPI](https://pypi.python.org/pypi/CoVeriTeam),
or one can simply clone this repository to use it.

### Dependencies

CoVeriTeam requires a machine with:
- Linux Ubuntu 18.04 (or 20.04)
- Python 3

Please make sure that namespaces and cgroups are configured as described in the
BenchExec [documentation](https://github.com/sosy-lab/benchexec/blob/main/doc/INSTALL.md).

### Reproduction Package
We have prepared an artifact archive for evaluation using
TACAS’22 Artifact Evaluation Virtual Machine for VirtualBox available
via [Zenodo](https://doi.org/10.5281/zenodo.5537146).

This archive is available [at Zenodo](https://doi.org/10.5281/zenodo.3813198).

## Links
* [Documentation](doc/index.md)
* [Competition help](doc/competition-help.md)
* [Tutorial](examples/README.md)
* [Changelog](CHANGELOG.md)
* [CoVeriTeam at PyPI](https://pypi.python.org/pypi/CoVeriTeam)

## License and Copyright

CoVeriTeam is licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0),
copyright [Dirk Beyer](https://www.sosy-lab.org/people/beyer/).
There are other artifacts in this repository
that are available under several other free licenses
(cf. [folder `LICENSES`](LICENSES)).

## Authors
Maintainer: [Sudeep Kanav](https://www.sosy-lab.org/people/kanav/)

Contributors:
- [Thomas Lemberger](https://www.sosy-lab.org/people/lemberger/)
- [Frederic Schönberger](https://gitlab.com/frederic.schoenberger)
- [Tobias Kleinert](https://github.com/Sowasvonbot)

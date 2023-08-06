<!--
This file is part of CoVeriTeam,
a tool for on-demand composition of cooperative verification systems:
https://gitlab.com/sosy-lab/software/coveriteam

SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

# Component-based CEGAR (c-CEGAR)

This directory contains different compositions of component-based CEGAR (c-CEGAR),
as described in the research paper
"Dirk Beyer, Jan Haltermann, Thomas Lemberger, Heike Wehrheim:
Decomposing Software Verification into Off-the-Shelf Components: An Application To CEGAR.
Proceedings of the 44th International Conference on Software Engineering (ICSE 2022).

The filename of each CVT file describes the exact composition defined by that file:
`cCegar-<exchange format>_cex-<feasibility checker>_ref-<precision refiner>.cvt`
As abstract model explorer, each composition uses CPAchecker with predicate analysis.

A usage example:

```
bin/coveriteam \
        examples/Component-based_CEGAR/cCegar-predmap_cex-cpachecker_ref-cpachecker.cvt \
        --data-model ILP32 \
        --input specification_path=examples/test-data/properties/unreach-call.prp \
        --input program_path=examples/test-data/c/error.i
```
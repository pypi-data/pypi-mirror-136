<!--
This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
https://gitlab.com/sosy-lab/software/coveriteam

SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

# Tutorial
This folder contains a few example compositions that can
be executed on test inputs using the script [./run_examples.sh](run_examples.sh).

**The examples can be executed individually by copying the command-lines from [run_examples.sh](run_examples.sh).**

## Validating Verifier
The CoVeriTeam program [validating-verifier.cvt](validating-verifier.cvt)
runs `UAutomizer` as a verifier on an example C program taken from the `sv-benchmarks` collection and
a reachability specification.
Then it runs `CPAchecker` as a validator using the verification witness produced by the verifier.

## Execution-Based Validation
Execution-based validation is an approach to result validation based on a violaion witness for a
reachability specification.
First, it transforms the given violation witness to a test case and then
executes the C program on the extracted test case to see if an `error` state is reached.
The file [execution-based-validation.cvt](execution-based-validation.cvt) contains
the CoVeriTeam program as discussed in the [literature](https://doi.org/10.1007/978-3-319-92994-1_1).

Following code snippet is taken from the file [execution-based-validation.cvt](execution-based-validation.cvt):
```code
w2test = ActorFactory.create(WitnessToTest, "../actors/cpachecker-witness-to-test.yml", "default");
testval = ActorFactory.create(TestValidator, "../actors/test-val.yml", "default");
spec_to_testspec = SpecToTestSpec();
execution_based_validator = SEQUENCE(PARALLEL(w2test, spec_to_testspec), testval);
```

We first extract a test case from a violation witness and then executes it to check whether
the specification is violated.
The validator is a sequential composition of two actors: a *witness-to-test converter*
(`Program`  &#215; `Specification` &#215; `Witness` &#8594; `TestSuite`,
and a test validator (`Program`  &#215; `Specification` &#215; `TestSuite` &#8594;  `Verdict`).
It uses *SpecToTestSpec*, a utility actor, to transform the safety
specification for verification to a test specification consumed by test validator.


## Reducer-Based Construction of a Conditional Model Checker
Conditional model checkers produce and consume conditions in additon to consuming only programs and specifications,
and producing only verdict and witness. [Reducers](https://doi.org/10.1145/3180155.3180259) can
be used to construct a conditonal model checker from an existing model checker, thus saving implementation effort.
A program reducer removes those paths
that were successfully verified already from the input program.
This residual program can then be given
to an off-the-shelf model checker for verification
that does not support input conditions.
The CoVeriTeam program [cmc-reducer.cvt](cmc-reducer.cvt) constructs and executes a
reducer-based conditional model checker.
Following code snippet is taken from this file:

```code
verifier = ActorFactory.create(ProgramVerifier, "../actors/uautomizer.yml", "default");
reducer = ActorFactory.create(CMCReducer, "../actors/cmc-reducer.yml", "default");
cmc = SEQUENCE(reducer, verifier);
```

This sequence of a program reducer and a model checker constructs
a conditional model checker.

# Examples and Applications
We have the following examples and applications:
- [Examples](tacas22_examples.sh) used in the article *On-Demand Composition of Cooperative Verification Systems* (to be) published in the TACAS'22 proceedings.
- [CondTest](CondTest/README.md): A CoVeriTeam implementation of [Conditional Testers](https://doi.org/10.1007/978-3-030-31784-3_11) 
- [MetaVal](MetaVal/README.md): A CoVeriTeam implementation of [MetaVal](https://doi.org/10.1007/978-3-030-53291-8_10)
- [component-based CEGAR (C-CEGAR)](Component-based_CEGAR/README.md): A decomposition of CEGAR, used and described in *Decomposing Software Verification into Off-the-Shelf Components: An Application to CEGAR*, (to be) published in the ICSE'22 proceedings.

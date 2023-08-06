<!--
This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
https://gitlab.com/sosy-lab/software/coveriteam

SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

# Verification-Based Validation à la MetaVal
`MetaVal` is a validator that user verifiers for validation.
To achieve this, it first instruments the input program with information from the witness,
and then uses an off-the-shelf verifier to verify the instrumented program.
Additionally, it first employs a simple selection algorithm 
to choose the verifier based on the specification.
The CoVeriTeam program [metaval.cvt](metaval.cvt)
constructs an actor that behaves similar to [MetaVal](https://gitlab.com/sosy-lab/software/metaval).
More details are available in the article [``MetaVal: Witness validation via verification''](https://doi.org/10.1007/978-3-030-53291-8_10).

## CoVeriTeam program for MetaVal
Following is a code snippet from the CoVeriTeam program for `MetaVal` and its explanation:

```python
// Select an appropriate verifier backend.
verifier_selector = ActorFactory.create(AlgorithmSelector, "../actors/algo-selector-metaval.yml", "default");
selected_verifier = execute(verifier_selector, input_for_algo_selection);

// First stage: instrumentation of witness and program.
ins = ActorFactory.create(WitnessInstrumentor, "../actors/cpa-witnesses-instrumentor.yml", "default");

// Second stage: use the verifier backend.
verifier_def = selected_verifier.actordef;
verifier = ActorFactory.create(ProgramVerifier, verifier_def);
metaval = SEQUENCE(ins, verifier);
```
The file [metaval.cvt](metaval.cvt) contains the above code.

First we create an actor for algorithm selector.
This actor takes a program` and a specification and produces an identifier for the selected verifier.
We execute the algorithm selector on the given input (program and specification)
to choose the verifier to be used in the composition.

`MetaVal` is a sequence of a witness instrumentor,
and a verifier based on the output of the algorithm selector.
After the selection, we create actors for witness instrumentor and the selected verifier.
The sequence of these two is MetaVal.

## Example Command
Following is an example command to execute `MetaVal` from this (`coveriteam/examples/MetaVal/`) directory:

```bash
../../bin/coveriteam metaval.cvt  \
 --input prog_path="../test-data/c/ConversionToSignedInt.i" \
 --input spec_path="../test-data/properties/no-overflow.prp" \
 --input witness_path="../test-data/witnesses/ConversionToSignedInt_nooverflow_witness.graphml" \
 --data-model ILP32
```

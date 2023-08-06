<!--
This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
https://gitlab.com/sosy-lab/software/coveriteam

SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

## Conditional Testing à la CondTest

Conditional testing is a cooperative test generation technique where
tester generates test cases and also outputs the summary of the work done in form of covered goals.
Another test generator can generate the test cases while making
use of this information, saving time to generate test cases for the already covered goals.

The CoVeriTeam programs [condtest.cvt](condtest.cvt), and [repeat-condtest.cvt](repeat-condtest.cvt)
contain implementations of conditional testers as described in the [literature](https://doi.org/10.1007/978-3-030-31784-3\_11).

## CoVeriTeam programs for Conditional Testing

### Conditional Testing&mdash;*sequence*
Following snippet of code shows the construction of a conditional tester in CoVeriTeam
taken from the file [condtest.cvt](condtest.cvt).

```code
fun conditional_tester(reducer, tester){
    // A sequence of reducer and the test generator.
    test_gen = SEQUENCE(reducer, tester);

    // Joiner takes the artifact type and input artifact names, and the name of the mergred artifact.
    joiner = Joiner(TestGoal, {'covered_goals', 'extracted_goals'}, 'covered_goals');
    extractor = ActorFactory.create(TestGoalExtractor, "../../actors/test-goal-extractor.yml", "latest");
    // Sequence of the extractor and joiner producing the set of goals covered by merging the input goals and extracted goals.
    ext_and_joiner = SEQUENCE(extractor, joiner);

    // Also forward the input test suite to output and accumulate.
    extractor_plus = PARALLEL(ext_and_joiner, Identity({'test_suite'}));

    // Conditional tester is a sequence of reducer, tester and extractor.
    ct = SEQUENCE(test_gen, extractor_plus);
    return ct;
}

// Instantiate the test generator and reducer (pruner in this case).
tester = ActorFactory.create(ProgramTester, tester_yml);
pruner = ActorFactory.create(TestGoalPruner, "../../actors/test-goal-pruner.yml", "latest");
ct = conditional_tester(pruner, tester);

// Instrumentor instruments the code with test goals for condtest.
instrumentor = ActorFactory.create(TestCriterionInstrumentor, "../../actors/test-criterion-instrumentor.yml", "latest");
condtest = SEQUENCE(instrumentor, ct);

```

The function `conditional_tester` composes a conditional tester
from a reducer and an off-the-shelf tester.
In this function, first a reducer and a tester are put in sequence named `test_gen`, i.e.,
the residual program is fed to the tester.
Then we create an extractor to extract the goals covered by the
test suite produced by the tester.
Then we create a *Joiner* to merge the initially covered goals and newly discovered covered goals.
Then we put the extractor and the joiner in a sequence named `ext_and_joiner`.
The type of this sequence is: `Program` &#215; `Specification` &#215; `TestSuite`  &#215; 
`Condition` 	&#8594; `Condition`.
In principle, a conditional tester is a sequence of `test_gen` and `ext_and_joiner`.
But since `ext_and_joiner` does not output a test suite,
and we want our conditional tester to output a test suite,
we use the *Identity* actor to forward the test suite from `test_gen`.
In line~12 we put the identity actor and `ext_and_joiner` in parallel composition,
and then put this parallel composition in sequence with `test_gen`
to get a conditional tester.
This construction of a conditional tester instruments the input program with 
labels to track the goals.
Thus, we place a 
*TestCriterionInstrumentor* before the conditional tester.


### Conditional Testing&mdash;*cyclic*
Following snippet of code shows the construction of a cyclic conditional tester in CoVeriTeam
taken from the file [repeat-condtest.cvt](repeat-condtest.cvt).

```code
// At first create a tester based on a verifier.
w2test = ActorFactory.create(WitnessToTest, "../../actors/cpachecker-witness-to-test.yml", "default");
ver = ActorFactory.create(ProgramVerifier, "../../actors/cpa-seq.yml", "default");
tester = SEQUENCE(ver, w2test);

// We use the annotator reducer in this case, and also we need to convert the test spec to a safety spec.
annotator = ActorFactory.create(TestGoalAnnotator, "../../actors/test-goal-annotator.yml", "latest");
test_spec_to_spec = TestSpecToSpec();
reducer = PARALLEL(annotator, test_spec_to_spec);

// Create a conditional tester based on the tester and reducer.
condtest = conditional_tester(reducer, tester);
rename_goals = Rename({'covered_goals': 'input_covered_goals'});

 // Repeat condtest till the there are not more covered goals, and accumulate the test suite.
tc = 'input_covered_goals' == 'covered_goals';
iter = REPEAT(tc, PARALLEL(rename_goals, condtest));

instrumentor = ActorFactory.create(TestCriterionInstrumentor, "../../actors/test-criterion-instrumentor.yml", "latest");
new_tester = SEQUENCE(instrumentor, iter);

```

At first, we compose a tester that generates test cases based on a witness produced by a 
verifier. 
We put a verifier and a witness to test generator in a sequence to 
create this tester. 
Later, this tester is called repeatedly, reducing the program in each iteration.

After creating a tester based on a verifier,
we create an *Annotator* reducer which
(i) annotates the program with 
*error* labels for the verifier to find the path to and
(ii) filters out the already covered goals, i.e., the condition, from the list of goals to be 
annotated. 
A *TestSpecToSpec* actor is used to convert a `TestSpecification` to a `Specification` for a verifier. 

Then, a conditional tester is created by composing the annotator reducer and a verifier 
based tester using the `conditional_tester` function described above.
Then this conditional tester is put in a `repeat` composition to be executed iteratively. 
The repeat cycle is terminated  when the `covered_goals` remains unchanged,
i.e., the conditional tester is executed till it can generate test cases that increase the coverage.
This composition will keep on accumulating the 
test suite generated in each iteration and finally output the collection of all 
the generated test suites.
Then analogously to the above, the *TestCriterionInstrumentor* is placed 
before the conditional tester to instrument the test criterion for goal tracking.


## Example Command

Following is an example command to execute CondTest from this (`coveriteam/examples/CondTest/`) directory:

```bash
 ../../bin/coveriteam condtest.cvt \
     --input tester_yml="../../actors/klee.yml" \
     --input prog="../test-data/c/test.c" \
     --input spec="../test-data/properties/coverage-branches.prp"
```

Following is an example command to execute cyclic CondTest from this (`coveriteam/examples/CondTest/`) directory:

```bash
../../bin/coveriteam repeat-condtest.cvt \
  --input prog_path="../test-data/c/Problem01_label15.c" \
  --input spec_path="../test-data/properties/coverage-branches.prp" \
  --data-model ILP32
```
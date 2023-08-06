#! /bin/bash

# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

# This script contains example commands for the examples used in the 
# TACAS 2022 article: On-Demand Composition of Cooperative Verification Systems

cd $(dirname $0)

echo "Running only a verifier (CPAchecker) using CoVeriTeam"
echo
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/cpa-seq.yml \
  --input verifier_version=default \
  --input program_path=test-data/c/Problem02_label16.c \
  --input specification_path=test-data/properties/unreach-call.prp \
  --data-model ILP32
echo

echo "########################################"
echo "Validating Verifier: Example 1. in the paper"
echo "########################################"
echo
../bin/coveriteam validating-verifier.cvt \
  --input verifier_path=../actors/cpa-seq.yml \
  --input verifier_version=default \
  --input validator_path=../actors/cpa-validate-violation-witnesses.yml \
  --input validator_version=default \
  --input program_path=test-data/c/Problem02_label16.c \
  --input specification_path=test-data/properties/unreach-call.prp \
  --data-model ILP32
echo

echo "########################################"
echo "Execution-Based Validation"
echo "########################################"
echo "Execution-Based Validation: A concrete test case is generated from a witness, and then this test is used to validate the alarm."
echo "If the test validator is able to validate then it returns true, i.e., it returns true if it can validate the alarm."
echo
../bin/coveriteam execution-based-validation.cvt \
  --input prog_path="test-data/c/Problem01_label15.c" \
  --input spec_path=test-data/properties/unreach-call.prp \
  --input witness_path="test-data/witnesses/Problem01_label15_reach_safety.graphml" \
  --data-model ILP32
echo

echo "########################################"
echo "Reducer-based construction of a conditional model checker"
echo "########################################"
echo
../bin/coveriteam reducer-based-conditional-model-checker.cvt \
  --input prog_path=test-data/c/slicingReducer-example.c \
  --input spec_path=test-data/properties/unreach-call.prp \
  --input cond_path="test-data/c/slicingCondition.txt" \
  --data-model ILP32
echo

echo "########################################"
echo "Conditional tester based on Klee: Fig. 7"
echo "########################################"
echo
echo "Execution of a conditional tester based on Klee."
../bin/coveriteam CondTest/condtest.cvt \
  --input prog_path="test-data/c/test.c" \
  --input tester_yml="../actors/klee.yml" \
  --input spec_path="test-data/properties/coverage-branches.prp" \
  --data-model ILP32
echo

echo "########################################"
echo "A verifier based tester. Not present in the paper explicitly."
echo "A tester that generates a test based on a witness produced by a verifier."
echo "########################################"
echo
echo "Execution of a tester based on a verifier."
../bin/coveriteam verifier-based-tester.cvt \
  --input prog_path="test-data/c/CostasArray-10.c" \
  --input spec_path=test-data/properties/unreach-call.prp \
  --data-model ILP32
echo

echo "########################################"
echo "Cyclic conditional tester: Fig. 8"
echo "The tester in this cyclic conditiona tester is based on a verifier."
echo "It will iteratively keep on generating test cases till it can."
echo "########################################"
echo
../bin/coveriteam CondTest/repeat-condtest.cvt \
  --input prog_path="test-data/c/test-repeat-condtest.c" \
  --input spec_path="test-data/properties/coverage-branches.prp" \
  --data-model ILP32
echo

echo "########################################"
echo "Verification-Based Validation (MetaVal): Fig. 9"
echo "########################################"
echo
../bin/coveriteam MetaVal/metaval.cvt \
  --input prog_path="test-data/c/ConversionToSignedInt.i" \
  --input spec_path="test-data/properties/no-overflow.prp" \
  --input witness_path="test-data/witnesses/ConversionToSignedInt_nooverflow_witness.graphml" \
  --data-model ILP32
echo

#! /bin/bash

# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

cd $(dirname $0)

echo "Running a verifier"
echo
echo "Verifier"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/cpa-seq.yml \
  --input verifier_version=default \
  --input program_path=test-data/c/Problem02_label16.c \
  --input specification_path=test-data/properties/unreach-call.prp \
  --data-model ILP32
echo

echo "Running CPAchecker"
echo
echo "Verifier"
../bin/coveriteam cpachecker.cvt \
  --input prog_path=test-data/c/Problem02_label16.c \
  --input spec_path=test-data/properties/unreach-call.prp \
  --data-model ILP32
echo

echo "Constructing and Executing Example Actors"
echo
echo "Validating Verifier"
../bin/coveriteam validating-verifier.cvt \
  --input verifier_path=../actors/cpa-seq.yml \
  --input verifier_version=default \
  --input validator_path=../actors/cpa-validate-violation-witnesses.yml \
  --input validator_version=default \
  --input program_path=test-data/c/Problem02_label16.c \
  --input specification_path=test-data/properties/unreach-call.prp \
  --data-model ILP32
echo

echo "Execution-Based Validation"
../bin/coveriteam execution-based-validation.cvt \
  --input prog_path="test-data/c/Problem01_label15.c" \
  --input spec_path=test-data/properties/unreach-call.prp \
  --input witness_path="test-data/witnesses/Problem01_label15_reach_safety.graphml" \
  --data-model ILP32
echo

echo "Execution-Based Validation Using a Witness Instrumentor"
../bin/coveriteam exe-validator-witness-instrument.cvt \
  --input prog_path=test-data/c/gcnr2008.i \
  --input spec_path=test-data/properties/unreach-call.prp \
  --input witness_path="test-data/witnesses/gcnr2008_violation_witness.graphml" \
  --data-model ILP32
echo

echo "Reducer-Based Construction of a Conditional Model Checker"
../bin/coveriteam reducer-based-conditional-model-checker.cvt \
  --input prog_path=test-data/c/slicingReducer-example.c \
  --input spec_path=test-data/properties/unreach-call.prp \
  --input cond_path="test-data/c/slicingCondition.txt" \
  --data-model ILP32
echo

echo "Conditional Testing"
../bin/coveriteam CondTest/condtest.cvt \
  --input prog_path="test-data/c/test.c" \
  --input tester_yml="../actors/klee.yml" \
  --input spec_path="test-data/properties/coverage-branches.prp" \
  --data-model ILP32
echo

echo "Verifier-Based Tester"
../bin/coveriteam verifier-based-tester.cvt \
  --input prog_path="test-data/c/CostasArray-10.c" \
  --input spec_path="test-data/properties/unreach-call.prp" \
  --data-model ILP32
echo

echo "Cyclic Conditional Testing"
../bin/coveriteam CondTest/repeat-condtest.cvt \
  --input prog_path="test-data/c/Problem01_label15.c" \
  --input spec_path="test-data/properties/coverage-branches.prp" \
  --data-model ILP32
echo

echo "Verification-Based Validation. MetaVal with algorithm selection."
../bin/coveriteam MetaVal/metaval.cvt \
  --input prog_path="test-data/c/ConversionToSignedInt.i" \
  --input spec_path="test-data/properties/no-overflow.prp" \
  --input witness_path="test-data/witnesses/ConversionToSignedInt_nooverflow_witness.graphml" \
  --data-model ILP32
echo

echo "Portfolio-based Verification."
../bin/coveriteam portfolio.cvt \
--input program_path=test-data/c/error.i \
--input specification_path=test-data/properties/unreach-call.prp \
--data-model ILP32
echo

echo "Portfolio in Portfolio Verification"
../bin/coveriteam portfolio-in-portfolio.cvt \
--input program_path=test-data/c/error.i \
--input specification_path=test-data/properties/unreach-call.prp \
--data-model ILP32
echo

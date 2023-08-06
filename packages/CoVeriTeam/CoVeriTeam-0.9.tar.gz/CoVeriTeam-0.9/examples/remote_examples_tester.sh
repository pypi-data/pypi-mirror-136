#! /bin/bash

# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

cd $(dirname $0)

echo "Running a tester"
echo
echo "FuSeBMC"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/fusebmc.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "cmaesfuzz"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/cmaesfuzz.yml \
  --input program_path=../../sv-benchmarks/c/reducercommutativity/rangesum.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-branches.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "coveritest"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/coveritest.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "HybridTiger"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/hybridtiger.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Klee"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/klee.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "legion"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/legion.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "libkluzzer"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/libkluzzer.yml \
  --input program_path=../../sv-benchmarks/c/float-benchs/sqrt_poly2.c \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "symbiotic"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/symbiotic-tester.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "tracerx"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/tracerx.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a tester"
echo
echo "verifuzz"
../bin/coveriteam tester.cvt \
  --input tester_path=../actors/verifuzz.yml \
  --input program_path=../../sv-benchmarks/c/list-ext-properties/list-ext.i \
  --input specification_path=../../sv-benchmarks/c/properties/coverage-error-call.prp \
  --data-model ILP32 \
  --remote
echo

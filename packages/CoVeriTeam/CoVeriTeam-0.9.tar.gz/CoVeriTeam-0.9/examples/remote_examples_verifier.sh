#! /bin/bash

# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

cd $(dirname $0)

#--------------------------- C Verifiers -------------------------
echo "Running a verifier"
echo
echo "2Ls"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/2ls.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "BRICK"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/brick.yml \
  --input program_path=../../sv-benchmarks/c/floats-cdfpl/newton_1_4.i \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "CBMC"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/cbmc.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "CPA-BAM-BnB"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/cpa-bam-bnb.yml \
  --input program_path=../../sv-benchmarks/c/ldv-linux-3.0/module_get_put-drivers-hid-hid-magicmouse.ko.cil.out.i \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "CPA-Lockator"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/cpa-lockator.yml \
  --input program_path=../../sv-benchmarks/c/pthread/lazy01.i \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "CPA-Seq"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/cpa-seq.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Dartagnan"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/dartagnan.yml \
  --input program_path=../../sv-benchmarks/c/pthread/lazy01.i \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "EBF"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/ebf.yml \
  --input program_path=../../sv-benchmarks/c/pthread/lazy01.i \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "DIVINE"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/divine.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "ESBMC-incr"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/esbmc-incr.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "ESBMC-kind"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/esbmc-kind.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "FramaC"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/frama-c-sv.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

# echo "Running a verifier"
# echo
# echo "GACAL"
# ../bin/coveriteam verifier.cvt \
#   --input verifier_path=../actors/gacal.yml \
#   --input program_path=../../sv-benchmarks/c/loops/count_up_down-2.c \
#   --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
#   --data-model ILP32 \
#   --remote
# echo

echo "Running a verifier"
echo
echo "Gazer-Theta"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/gazer-theta.yml \
  --input program_path=../../sv-benchmarks/c/bitvector/byte_add_1-1.i \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Goblint"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/goblint.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test01.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Korn"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/korn.yml \
  --input program_path=../../sv-benchmarks/c/recursive/Ackermann02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Lazy-CSeq"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/lazycseq.yml \
  --input program_path=../../sv-benchmarks/c/pthread/lazy01.i \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

# echo "Running a verifier"
# echo
# echo "Map2Check"
# ../bin/coveriteam verifier.cvt \
#   --input verifier_path=../actors/map2check.yml \
#   --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
#   --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
#   --data-model ILP32 \
#   --remote
# echo

echo "Running a verifier"
echo
echo "PeSCo"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/pesco.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "PInaka"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/pinaka.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "PredatorHP"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/predatorhp.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Smack"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/smack.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Symbiotic"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/symbiotic.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "Uautomizer"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/uautomizer.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "UKojak"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/ukojak.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "UTaIpan"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/utaipan.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

echo "Running a verifier"
echo
echo "VeriAbs"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/veriabs.yml \
  --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
  --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
  --data-model ILP32 \
  --remote
echo

# echo "Running a verifier"
# echo
# echo "VeriFuzz"
# ../bin/coveriteam verifier.cvt \
#   --input verifier_path=../actors/verifuzz.yml \
#   --input program_path=../../sv-benchmarks/c/ldv-regression/test02.c \
#   --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
#   --data-model ILP32 \
#   --remote
# echo

# echo "Running a verifier"
# echo
# echo "Yogar-CBMC"
# ../bin/coveriteam verifier.cvt \
#   --input verifier_path=../actors/yogar-cbmc.yml \
#   --input program_path=../../sv-benchmarks/c/pthread/lazy01.i \
#   --input specification_path=../../sv-benchmarks/c/properties/unreach-call.prp \
#   --data-model ILP32 \
#   --remote
# echo

#--------------------------- Java Verifiers -------------------------
echo "Running a verifier"
echo
echo "COASTAL"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/coastal.yml \
  --input program_path=../../sv-benchmarks/java/jayhorn-recursive/Ackermann01 \
  --input program_path=../../sv-benchmarks/java/common \
  --input specification_path=../../sv-benchmarks/java/properties/assert.prp \
  --remote
echo

echo "Running a verifier"
echo
echo "Java-Ranger"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/java-ranger.yml \
  --input program_path=../../sv-benchmarks/java/jayhorn-recursive/Ackermann01 \
  --input program_path=../../sv-benchmarks/java/common \
  --input specification_path=../../sv-benchmarks/java/properties/assert.prp \
  --remote
echo

echo "Running a verifier"
echo
echo "JayHorn"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/jayhorn.yml \
  --input program_path=../../sv-benchmarks/java/jayhorn-recursive/Ackermann01 \
  --input program_path=../../sv-benchmarks/java/common \
  --input specification_path=../../sv-benchmarks/java/properties/assert.prp \
  --remote
echo

echo "Running a verifier"
echo
echo "JBMC"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/jbmc.yml \
  --input program_path=../../sv-benchmarks/java/jayhorn-recursive/Ackermann01 \
  --input program_path=../../sv-benchmarks/java/common \
  --input specification_path=../../sv-benchmarks/java/properties/assert.prp \
  --remote
echo

echo "Running a verifier"
echo
echo "JDart"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/jdart.yml \
  --input program_path=../../sv-benchmarks/java/jayhorn-recursive/Ackermann01 \
  --input program_path=../../sv-benchmarks/java/common \
  --input specification_path=../../sv-benchmarks/java/properties/assert.prp \
  --remote
echo

echo "Running a verifier"
echo
echo "spf"
../bin/coveriteam verifier.cvt \
  --input verifier_path=../actors/spf.yml \
  --input program_path=../../sv-benchmarks/java/jayhorn-recursive/Ackermann01 \
  --input program_path=../../sv-benchmarks/java/common \
  --input specification_path=../../sv-benchmarks/java/properties/assert.prp \
  --remote
echo

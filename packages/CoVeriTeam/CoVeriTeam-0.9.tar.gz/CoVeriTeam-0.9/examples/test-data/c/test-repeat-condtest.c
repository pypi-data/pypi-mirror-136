// This file is redistributed as part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
// https://gitlab.com/sosy-lab/software/coveriteam
//
//
// SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
//
// SPDX-License-Identifier: Apache-2.0

extern int __VERIFIER_nondet_int();
void assume(int cond) {
  if (!cond)
    abort();
}

int main() {
      int i = __VERIFIER_nondet_int();
      int j = __VERIFIER_nondet_int();
      assume(i<10 && i> 0);
      assume(j<10 && j> 0);
      if (i < 5){

      }
      else{

      }
      int k = __VERIFIER_nondet_int();
      if (j < 5){

      }
      
}

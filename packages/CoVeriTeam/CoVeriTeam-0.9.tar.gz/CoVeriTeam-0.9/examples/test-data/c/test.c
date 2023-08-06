// This file is redistributed as part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
// https://gitlab.com/sosy-lab/software/coveriteam
//
// This file has been taken from the sv-benchmarks repository: https://github.com/sosy-lab/sv-benchmarks
//
// SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
//
// SPDX-License-Identifier: Apache-2.0

extern void __VERIFIER_error();
extern unsigned int __VERIFIER_nondet_uint();
extern _Bool __VERIFIER_nondet_bool();
extern void __VERIFIER_assume();

int main() {
      int a = get_new(5);
      a = get_new(a);
      _Bool b = __VERIFIER_nondet_bool();
      _Bool c = __VERIFIER_nondet_bool();
      while(a) {
            __VERIFIER_assume((b || c) && (!b || !c));
            b = !b;
            c = !c;
            if (b != 1 && c != 1) {
                  ERROR: __VERIFIER_error();
            }
            a--;
      }
}

void foo() {
      int a = 5;
}

int get_new(int a) {
      a++;
      return a;
}
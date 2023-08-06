// This file is redistributed as part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
// https://gitlab.com/sosy-lab/software/coveriteam
//
// This file has been taken from the sv-benchmarks repository: https://github.com/sosy-lab/sv-benchmarks
//
// SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
//
// SPDX-License-Identifier: Apache-2.0

unsigned char __VERIFIER_nondet_uchar(void);
void __VERIFIER_error();
void __VERIFIER_assume(int cond);

void __VERIFIER_error() {

}

int main() {
  unsigned int sum = 0;
  unsigned long long prod = 1;

  unsigned char n = __VERIFIER_nondet_uchar();
  int i = 1;
  while (i < n) {
    sum = sum + i;
    prod = prod * i;
    i = i + 1;
  }
  if (!(sum >= 0)) __VERIFIER_error();
  if (!(prod >= 0)) __VERIFIER_error();
}

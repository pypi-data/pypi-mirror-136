// This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
// https://gitlab.com/sosy-lab/software/coveriteam
//
// SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
//
// SPDX-License-Identifier: Apache-2.0

#include <assert.h>
void reach_error() { assert(0); }
extern int __VERIFIER_nondet_int(void);

int main()
{
    // default output
    int output = -1;

    // main i/o-loop
    while(1)
    {
        if (__VERIFIER_nondet_int()) reach_error();
    }
}

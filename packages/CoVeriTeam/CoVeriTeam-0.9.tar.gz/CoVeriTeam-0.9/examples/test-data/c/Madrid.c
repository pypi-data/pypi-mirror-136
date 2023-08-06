// This file is redistributed as part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
// https://gitlab.com/sosy-lab/software/coveriteam
//
// This file has been taken from the sv-benchmarks repository: https://github.com/sosy-lab/sv-benchmarks
//
// SPDX-FileCopyrightText: 2013 University of Freiburg
//
// SPDX-License-Identifier: BSD-2-Clause

/*
 * Date: 2013-05-02
 * Author: heizmann@informatik.uni-freiburg.de
 *
 */
typedef enum {false, true} bool;

extern int __VERIFIER_nondet_int(void);

int main()
{
    int x;
	x = 7;
	while (true) {
		x = 2;
	}
	return 0;
}

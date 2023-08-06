// This file is redistributed as part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
// https://gitlab.com/sosy-lab/software/coveriteam
//
// This file has been taken from the sv-benchmarks repository: https://github.com/sosy-lab/sv-benchmarks
//
// SPDX-FileCopyrightText: 2014 RWTH Aachen University
//
// SPDX-License-Identifier: BSD-2-Clause

 char *(cstrcat)(char *s1, const char *s2)
 {
     char *s = s1;
     /* Move s so that it points to the end of s1.  */
     while (*s != '\0')
         s++;
     /* Do the copying in a loop.  */
     while ((*s++ = *s2++) != '\0')
         ;               /* The body of this loop is left empty. */
     /* Return the destination string.  */
     return s1;
 }

int main() {
  char *s1;
  char *s2;
  cstrcat(s1, s2);
  return 0;
}

<!--
This file is part of CoVeriTeam,
a tool for on-demand composition of cooperative verification systems:
https://gitlab.com/sosy-lab/software/coveriteam

SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

## CoVeriTeam 0.9
* Examples used in the article *On-Demand Composition of Cooperative Verification Systems* (to be) published in the TACAS'22 proceedings. 
* New composition: `Parallel_Portfolio`. It allows to put multiple actors in a parallel portfolio.
  The actors are executed in parallel and the results of the first one that finishes satisfying the success condition are selected.
* New case study: component-based CEGAR (C-CEGAR), described and used in the article *Decomposing Software Verification into Off-the-Shelf Components: An Application to CEGAR*, (to be) published in the ICSE'22 proceedings.


## CoVeriTeam 0.6
* New format for actor definition YAML.
  It allows to define multiple versions of the tool archive, and then select one of them when creating the actor.
* A new mode for tool execution (trusted mode) that allows the tools to be executed with lighter container configuration.
* A new parameter to disable cache update. When this parameter is set then CoVeriTeam will not try to download the tool.
  If the tool is available in cache then it is executed otherwise CoVeriTeam exits with an error message.
  It is useful for creating self contained archives of the tools based on CoVeriTeam.
  


## CoVeriTeam 0.5
* Added actor definitions for the verifiers from software verification competition 2020
* Renamed the folder containing actor definitions from config to actors

## CoVeriTeam 0.4
* Execution with [BencheExec](https://github.com/sosy-lab/benchexec)
* MetaVal implemented using CoVeriTeam
* Template for input artifacts in the actorsuration YAML file.

## CoVeriTeam 0.3
* New Actors:
  1. algorithm selection actor,
  2. dynamic (or lazy) actor which instantiates the concrete actor during runtime based on an actor definition.
* Grammar:
  1. support for print statement
  2. unicode characters in comments.
* YAML: support for include in yaml files.
* Tool Info module can now be also provided by a url.

## CoVeriTeam 0.2
* New formal for YAML file
* setting up PyPi release

## CoVeriTeam 0.1
Initial version of CoVeriTeam as available on Zenodo: https://doi.org/10.5281/zenodo.3818283

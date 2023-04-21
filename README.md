# tools
A set of tools created to aid working on the Ensembl project, mostly written in python

## codeflares

A rough script that pulls out code comments that look like coder flares ("todo","hack""fixme","bug") - currently hardcoded for typescript ('*.ts, *.tsx').

## cbor2-decomp

Two scripts, one that decodes cbor2 files (EARDO for example) and another for [HAR files](https://en.wikipedia.org/wiki/HAR_(file_format))

## personalisues

A python module with CLI that pulls out active (`status not in (Done, Closed, Resolved, Cancelled)`) tickets for a set of people and generates a JSON report.

## storeyreview

An attempt at pulling out metrics on JIRA sprints - :fire: do not use :fire: This module attempts to recreate Jira's sprint reports with additional information. 
Sadly it has proven very difficult to achieve. I plan to switch to using the undocumented API that Jira uses for sprint reports.
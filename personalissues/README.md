# Personal Issues

A python module with CLI that pulls out active (`status not in (Done, Closed, Resolved, Cancelled)`) tickets for a set of people and generates a JSON report.

```
%  poetry run python -m personalissues --help >>
Personal Issues - gathers metrics on JIRA tickets assigned to one or more users

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        API token
  -o OUTPUT, --output OUTPUT
                        Name of file to output results (JSON)
  -j HOST, --host HOST  Jira host
  -p [PEOPLE [PEOPLE ...]], --people [PEOPLE [PEOPLE ...]]
                        People to report on (1 or more)
  -l LIMIT, --limit LIMIT
                        Limit to a specific project
  -s SUMMARY, --summary SUMMARY
                        Generate or update user counts summary
```

## Install

1. git clone
2. cd personalissues
3. poetry install
4. poetry run python -m personalissues --help

## Notice
:fire:
This module is still being worked on and is likely to change. I am currently working on a jupyter notebook to make it easier to view the progress of any given project. This notebook will be avaliable  in this repo once it is closer to being useful. 
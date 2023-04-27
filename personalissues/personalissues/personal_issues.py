import sys
import os
import json
import csv
import math
from datetime import datetime, timedelta
from argparse import ArgumentParser

from personalissues.jira import get_issues_for_person, get_issue_comment, get_jira_connection, get_unassigned_issues

# What do we want? 
# - Track peoples progress at a set time each week
#   - Count tickets assigned, tickets closed, average ticket life
# - Provide details of open tickets 
# - Do so for all desired projects

# - https://jira.readthedocs.io/examples.html#comments
# - new mode - update issue count

# Notebook stuff 
# - https://www.digitalocean.com/community/tutorials/data-analysis-and-visualization-with-pandas-and-jupyter-notebook-in-python-3
# - https://medium.com/@mjspeck/presenting-code-using-jupyter-notebook-slides-a8a3c3b59d67

JIRA_URL = "https://www.ebi.ac.uk/panda/jira"

def getCLICommands(): 
    parser = ArgumentParser(
        description="Personal Issues - gathers metrics on JIRA tickets assigned to one or more users",
        usage="python -m personalissues -t TOKEN -p imran andrey jyo jon -o frontend.json -l ENSWEB --summary true"
    )
     
    parser.add_argument(
        "-t",
        "--token",
        required=True,
        help = "API token"
    )
    
    parser.add_argument(
        "-o",
        "--output",
        default="personal_issues.json",
        required=True,
        help="Name of file to output results (JSON)"
    )
    
    parser.add_argument(
        "-j",
        "--host",
        default = JIRA_URL, 
        help = "Jira host"
    )
    
    parser.add_argument( 
        "-p",
        "--people",
        required=True, 
        nargs="*",
        help="People to report on (1 or more)"
    )
    
    parser.add_argument(
        "-l",
        "--limit",
        help="Limit to a specific project"
    )
    
    parser.add_argument(
        "-s",
        "--summary",
        help="Generate or update user counts summary"
    )
    
    return parser

def chop_iso_datetime(datetime):
    if "T" in datetime:
        return datetime.split("T")[0]
    return datetime
    
def clean_sprint_datetime(sprint_date): 
    return datetime.fromisoformat(sprint_date[:sprint_date.rfind(".")]) # I should handle this better
    
def get_life_time_for_issue(created_date_str): 
    created_date = clean_sprint_datetime(created_date_str)
    now = datetime.today()
    return (now - created_date).days
    
def get_last_comment(jira_conn, issue, comments): 

    comment_list = [comment for comment in comments]
    if len(comment_list) == 0: 
        return "No comment"
    
    comment = get_issue_comment(jira_conn, issue, comment_list[-1])
    return comment.body

def generate_summary(file, flattened_issues):
    people = {}
    last_run = {}

    for issue in flattened_issues: 
        status = issue['status']
        if ' ' in status:
            status.replace(' ','_')
        
        if issue['person'] not in people:
           print(f"Found {issue['person']}")
           people[issue['person']] = {
               'issues':{
                   'total':0
               },
               'stats':{
                    'sum_life_times':0,
                    'avg_life_times':0
               }
           } 
        
        people[issue['person']]['issues']['total'] += 1
        people[issue['person']]['stats']['sum_life_times'] += issue['life']
        
        if status not in people[issue['person']]['issues']:
            people[issue['person']]['issues'][status] = 0

        people[issue['person']]['issues'][status] += 1
    
    #average issue life
    for person, counts in people.items():
        if person in last_run:
            dif_keys = [key for key in counts.keys() if key.endswith(dif_suffix)]
        
            for key in dif_keys:
                target = key[:len(key) - len(dif_suffix)]
                counts[key] = counts[target] - last_run[person][target]
        
        people[person]['stats']['avg_life_times'] = math.floor(
            people[person]['stats']['sum_life_times'] / people[person]['issues']['total'])
    
    with open(file,"w") as report:
        report.write(json.dumps(people, indent=4))
    
def _flatten_issue(issue, owner, jira_conn):
    return {
        'person':owner, 
        'issue':issue.key,
        'project':str(issue.fields.project),
        'summary':issue.fields.summary,
        'last_comment': get_last_comment(
                            jira_conn, 
                            issue.key, 
                            issue.fields.comment.comments
                        ),
        'status':str(issue.fields.status),
        'created':chop_iso_datetime(str(issue.fields.created)),
        'updated':chop_iso_datetime(str(issue.fields.updated)),
        'life': get_life_time_for_issue(issue.fields.created),
    }

def personal_issues(host, token, people, limit, output, summary): 
    print("Personal issues")
    print(f"Connecting to {host}")
    
    #remove file type
    if '.' in output:
        output = output.split('.')[0]
    
    # connect to jira 
    jira_conn = get_jira_connection(host, token)
    
    # get issues
    issues = get_issues_for_person(jira_conn, people)
    print("issues")
    flattened = []
    for person,issue_list in issues.items():
        
        flattened_issues = [_flatten_issue(issue, person, jira_conn) for issue in issue_list]
        flattened.extend(flattened_issues)
    
    if limit:
        print(f"Getting unassigned and filtering by project {limit}")
        issues = get_unassigned_issues(jira_conn, [limit])
        flattened_issues = [_flatten_issue(issue,'unassigned', jira_conn) for issue in issues[limit]] #Hardcoded to take one project for now
        flattened.extend(flattened_issues)
        flattened = [issue for issue in flattened if limit == issue['project']]
        
    if summary:
        generate_summary(f"{output}_summary.json", flattened)
        
    with open(f"{output}.json",'w') as json_file: 
        json_file.write(json.dumps(flattened, indent=4))
    print("Done :D")
        

def personal_issues_cli(args): 
    cli = getCLICommands().parse_args(args)
    personal_issues(cli.host, cli.token, cli.people, cli.limit, cli.output, cli.summary)
    

if __name__ == "__main__": 
    personal_issues_cli(sys.argv[1:])
import json
import configparser

import pandas as pd
from datetime import datetime

from personalissues.personal_issues import personal_issues

DATA_FILE = "frontend-ensweb"
ISSUES_FILE = "{}.json"
SUMMARY_FILE = "{}_summary.json"

def update_data(project, people, token):

    personal_issues(
        "https://www.ebi.ac.uk/panda/jira",
        token,
        people,
        project,
        project,
        True
    )

def load_data(project):
    with open(ISSUES_FILE.format(project)) as issue_file:
        issues = json.load(issue_file)
    
    print(f"{project}: {len(issues)} issues found")
    
    with open(SUMMARY_FILE.format(project)) as summary_file:
        summary = json.load(summary_file)
    
    print(f"{project}: Summary data found for {len(summary)} people")
    return issues, summary

def build_personal_load(project):
    
    issues, summary = load_data(project)

    counts = {}
    people_counts = {}
    
    view = []
    
    for person, data in summary.items():
        person_count = {key:value for key,value in data['issues'].items()}
        
        for key,value in person_count.items():
            if key not in counts:
                counts[key] = 0
                
            if person != 'unassigned':
                counts[key] += value
            
        people_counts[person] = person_count
    
    
    fields = [key for key,_ in counts.items()]
    
    for person, data in people_counts.items():
        flattened = [person]
        flattened.extend([data.get(key,0) for key in fields])
        view.append(flattened)
        
    flattened = ["Everyone"]
    flattened.extend([value for _, value in counts.items()])
    view.append(flattened)
    
    columns = ["Who"]
    columns.extend(fields)
    
    df = pd.DataFrame(view, columns = columns)

    return df

def build_assigned_tickets(project, person = "unassigned"):
    issues, _ = load_data(project)
    count = 0
    delta = 0
    for issue in issues:
        if issue["person"] == person:
            count += 1
    return count, delta
    
#----------------
def build_all_assigned_tickets(person, projects):
    count = 0
    delta = 0
    for project in projects:
        c,d = build_assigned_tickets(project, person)
        count += c
        delta += d
    return count, delta
        
    

#---------------
def build_issues(project):
    issues, summary = load_data(project)
    columns = ['issue','summary','person','release','sprint','status','life']
    
    LINK_FORMAT = "<a target=\"new\" href=\"https://www.ebi.ac.uk/panda/jira/browse/{id}\">{id}</a>"
    
    view = []
    for issue in issues:
        view.append([issue[key] for key in columns])
        
    for row in view:
        row[0] = LINK_FORMAT.format(id=row[0])

    df = pd.DataFrame(view, columns=columns)
    return df
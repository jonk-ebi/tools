from enum import Enum

import json
import configparser

import pandas as pd
from datetime import datetime

from personalissues.personal_issues import personal_issues

DATA_FILE = "frontend-ensweb"
ISSUES_FILE = "{}.json"
SUMMARY_FILE = "{}_summary.json"

UNASSIGNED = "unassigned"

"""
I want to store 
- last update
- last values for all metrics
- 
"""

class Data(Enum):
    All = 1,
    Issues = 2,
    Summary = 3,

class JiraData():
    def __init__(self, projects): 
        self.summary = {} 
        self.issues = {}
        self.metrics = {}
        self.projects = {}
        
        for project in projects:
            self.summary[project] = self.load_data(project,Data.Summary)
            self.issues[project] = self.load_data(project, Data.Issues)

    def update_data(self, project, people, token):
    
        personal_issues(
            "https://www.ebi.ac.uk/panda/jira",
            token,
            people,
            project,
            project,
            True
        )
    
    def load_data(self, project, data:Data):
        
        if data == Data.All or data == Data.Issues:
            with open(ISSUES_FILE.format(project)) as issue_file:
                issues = json.load(issue_file)
            print(f"{project}: {len(issues)} issues found")
        
        if data == Data.All or data == Data.Summary:
            with open(SUMMARY_FILE.format(project)) as summary_file:
                summary = json.load(summary_file)
            
            print(f"{project}: Summary data found for {len(summary)} people")
        
        if data == Data.All: 
            return issues, summary
        if data == Data.Issues: 
            return issues 
        if data == Data.Summary: 
            return summary
    
    def build_personal_load(self, project):
        
        summary = self.summary[project]
    
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
    
    #-------------
    
    def count_project_tickets_assigned_for_a_person(self, project, person=UNASSIGNED): 
        issues = self.issues[project]
        count = 0
        for issue in issues:
            if issue["person"] == person:
                count += 1
        return count
        
    def count_tickets_assigned_for_a_person(self, projects, person=UNASSIGNED):
        count = 0
        for project in projects:
            count += self.count_project_tickets_assigned_for_a_person(project, person)
        return count
        
    def build_assigned_project_tickets(self, project, person=UNASSIGNED):
        current_count = self.count_project_tickets_assigned_for_a_person(project, person)
        return current_count, 0
        
    def build_tickets_assigned_for_a_person(self, projects, person=UNASSIGNED):
        current_count = self.count_tickets_assigned_for_a_person(projects, person)
        return current_count, 0
    
    #---------------
    def build_issues(self, project):
        issues = self.issues[project]
        columns = ['issue','summary','person','release','sprint','status','life']
        
        LINK_FORMAT = "<a target=\"new\" href=\"https://www.ebi.ac.uk/panda/jira/browse/{id}\">{id}</a>"
        
        view = []
        for issue in issues:
            view.append([issue[key] for key in columns])
            
        for row in view:
            row[0] = LINK_FORMAT.format(id=row[0])
    
        df = pd.DataFrame(view, columns=columns)
        return df
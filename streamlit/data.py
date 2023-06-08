import os
import json
import configparser

from enum import Enum

import pandas as pd
from datetime import datetime

from personalissues.personal_issues import personal_issues

DATA_FILE = "frontend-ensweb"
ISSUES_FILE = "{}.json"
SUMMARY_FILE = "{}_summary.json"
METRIC_FILE = "metrics.json"

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
        
        self._load_metrics()

    def update_data(self, project, people, token):
    
        personal_issues(
            "https://www.ebi.ac.uk/panda/jira",
            token,
            people,
            project,
            project,
            True
        )
    
    def _load_metrics(self):
        if os.path.exists(METRIC_FILE):        
            with open(METRIC_FILE) as metricsStream:
                self.metrics = json.load(metricsStream)
    
    def _save_metrics(self):
        with open(METRIC_FILE, "w") as metricsStream:
            print(self.metrics)
            metricsStream.write(json.dumps(self.metrics, indent=4))
            
    def save_data(self):
        self._save_metrics()
            
    
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
    
    def _get_metric_delta(self, type, key, current_value ):
        if type not in self.metrics:
            self.metrics[type] = {}
            
        if key not in self.metrics[type]:
            print("Added new")
            self.metrics[type][key] = current_value
            
        delta = current_value - self.metrics[type][key]
        if delta == 0:
            delta = None # prevents the up zero delta
        print(f"{type}-{key}: {delta}")
        self.metrics[type][key] = current_value
        return delta
    
    
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
        delta = self._get_metric_delta("project_count",project, current_count)
        return current_count, delta
        
    def build_tickets_assigned_for_a_person(self, projects, person=UNASSIGNED):
        current_count = self.count_tickets_assigned_for_a_person(projects, person)
        delta = self._get_metric_delta("person_count",person, current_count)
        return current_count, delta
    
    #---------------
    def build_issues(self, project):
        issues = self.issues[project]
        columns = ['issue','summary','person','release','sprint','status','life','assigned','times_assigned']
        
        LINK_FORMAT = "<a target=\"new\" href=\"https://www.ebi.ac.uk/panda/jira/browse/{id}\">{id}</a>"
        
        view = []
        for issue in issues:
            view.append([issue[key] for key in columns])
            
        for row in view:
            row[0] = LINK_FORMAT.format(id=row[0])
    
        df = pd.DataFrame(view, columns=columns)
        return df
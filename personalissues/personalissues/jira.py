import sys
from datetime import datetime, timedelta
from jira import JIRA

FIELDS_OF_INTREST = ["sprint","status","description", "resolution"]
FIELD_SPRINT = FIELDS_OF_INTREST[0]
FIELD_STATUS = FIELDS_OF_INTREST[1]

SPRINT_END_CORRECTION_DELTA = timedelta(minutes=-1)

def iso_datetime_without_timezone(date): 
    return date[:date.rfind("+")]
    
def get_jira_connection(url, token):
    return JIRA(
        server=url,
        token_auth=token
    )
    
def get_issue_comment(jira, issue, id): 
    return jira.comment(issue,id)

def get_unassigned_issues(jira, projects): 
    issues = {}

    for project in projects:
        query = f"project = {project} AND assignee  is EMPTY  AND status not in (Done, Closed, Resolved, Cancelled) order by updated DESC"
        print(f"Query: {query}")
        issues[project] = jira.search_issues(query)

    return issues

def get_issues_for_person(jira, people): 

    issues = {}
    # Join together all the people into a single query, we don't need to spit by people as they get flattened
    for person in people:
        query = f"assignee = {person} AND status not in (Done, Closed, Resolved, Cancelled) order by updated DESC"
        print(f"Query: {query}")
        issues[person] = jira.search_issues(query)

    return issues
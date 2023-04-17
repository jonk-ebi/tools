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

def get_issues_for_person(jira, people): 

    issues = {}
    for person in people:
        query = f"assignee = {person} AND status not in (Done, Closed, Resolved, Cancelled) order by updated DESC"
        print(f"Query: {query}")
        issues[person] = jira.search_issues(query)

    return issues
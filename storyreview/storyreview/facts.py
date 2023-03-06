from datetime import datetime, timedelta
from statistics import median, mode, mean

# What do I really want to know? 
     # - PI How long do issues normally last - V, including, excluding cancelled - done
     # - Ag How many get cancelled - V -
     # - PI How many sprints do issues go through - V
     # - Ag How many issues sprints start with  - V - done
     # - Ag How many issues are added in the sprint - V - done
     # - Ag How many issues are cancelled in a sprint - V - done
     # - Ag How many issues remain in a sprint  - done
     # - Comments per issue / sprint - later 
     # - deep dive, average time in each status - later
     
     # For 2023-01 
     # "sprint_total_issues_count": 17, <- off by one 
     #  "sprint_issues_added_after_count": 10, <- off by 7 
     # "sprint_starting_issue_count": 13, <- correct 
     # "sprint_issues_done": 8 <- correct
#----
    # times from history.created
    # record item.field sprint -> records changing sprint - item toString fromString
    # record item.field status -> records swim lane movement - item toString fromString
    # record item.field description -> just count 
    # issues added to sprints mid sprint 
    # issues removed from sprints mid sprint
    # issues remaining at the end of a sprint 
    # number of issues a sprint starts with
    # dragged issues - https://community.atlassian.com/t5/Jira-Software-questions/Cancelled-issues-dragged-on-from-sprint-to-sprint/qaq-p/1019310


FINISHED_STATUSES = ["done", "closed", "resolved", "cancelled", "unresolved"]

CANCELLED_STATE = FINISHED_STATUSES[-1]
DONE_STATE = FINISHED_STATUSES[0]
IGNORE_STATES = FINISHED_STATUSES[1:]

ISSUE_FACTS = {} # Holds dictionary of issue fact functions, populated by is_fact
SPRINT_FACTS = {} 
ISSUE_TOTALS = {}

PADDING_DELTA = timedelta(hours = 23)

def is_issue_fact(fact): 
    ISSUE_FACTS[fact.__name__] = fact
    return fact

def is_sprint_fact(fact): 
    SPRINT_FACTS[fact.__name__] = fact
    return fact

def is_issue_total(fact): 
    ISSUE_TOTALS[fact.__name__] = fact
    return fact
          
def clean_sprint_datetime(sprint_date): 
    return datetime.fromisoformat(sprint_date[:sprint_date.rfind(".")]) # I should handle this better
          
@is_issue_fact
def issue_life_span(issue, issue_details): 
    if issue_details['status']['value'].lower() in FINISHED_STATUSES:
        created_date = datetime.fromisoformat(issue_details['common']['created'])
        closed_date = datetime.fromisoformat(issue_details['status']['occured'])
        gap = (closed_date - created_date).days
        if gap == 0: 
            gap += 1
        return gap
    return None

@is_issue_fact
def issue_end_status(issue, issue_details): 
    if issue_details['status']["value"].lower() in FINISHED_STATUSES:
        return issue_details['status']['value'].lower()
    return None
    
@is_issue_fact
def issue_number_of_sprints(issue, issue_details): 
    return issue_details['sprint']['value'].split(',')

@is_sprint_fact
def sprint_issues_cancelled(issue, issue_details, sprint_start, sprint_end, sprint):
    if issue_details['status']['value'].lower() == CANCELLED_STATE: 
        cancelled_date = datetime.fromisoformat(issue_details['status']['occured'])
        return 1
    return 0
  
@is_sprint_fact
def sprint_total_issues_count(issue, issue_details, sprint_start, sprint_end, sprint):
    if issue_details["status"]["value"] in IGNORE_STATES:
        return 0
    return 1
    
@is_sprint_fact
def sprint_starting_issue_count(issue, issue_details, sprint_start, sprint_end, sprint): 
    
    if issue_details["status"]["value"] in IGNORE_STATES:
        return 0
           
    add_to_sprint_date = datetime.fromisoformat(issue_details["sprint"]['occured'])
    if sprint_start <= add_to_sprint_date: 
        return 1
    return 0
    
@is_sprint_fact
def sprint_issues_added_after_count(issue, issue_details, sprint_start, sprint_end, sprint):
    if issue_details["status"]["value"] in IGNORE_STATES:
        return 0
        
    add_to_sprint_date = datetime.fromisoformat(issue_details['sprint']['occured'])
    if sprint_start <= add_to_sprint_date: 
        return 0
    return 1

@is_sprint_fact
def sprint_issues_done(issue,issue_details, sprint_start, sprint_end, sprint):
    if issue_details["status"]["value"] == DONE_STATE: 
        #print(issue)
        #print(issue_details["status"])
        #print('%' * 30)
        return 1
    return 0
               
@is_issue_total
def total_average_issue_life(issues): 
    done_issues = [
        issue[issue_life_span.__name__] for issue in issues
        if issue_end_status.__name__ in issue and issue[issue_end_status.__name__] == DONE_STATE
        ]
    if len(done_issues) == 0:
        return {
             "median":0,
            "mode":0,
            "mean":0
        }
    
    return {
        "median":median(done_issues),
        "mode":mode(done_issues),
        "mean":mean(done_issues)
    }

@is_issue_total
def total_issue_counts(issues): 
    issue_states = {}
    issue_states['total'] = len(issues)
    issue_states['open'] = 0
    
    for issue in issues:
        if issue_life_span.__name__ in issue:
            state = issue[issue_end_status.__name__]
            if state not in issue_states:
                issue_states[state] = 0
            issue_states[state] += 1
        else:
            issue_states['open'] += 1
    return issue_states

def get_issue_facts(issues, sprint):
    issue_facts = {}
    sprint_facts = {}

    sprint_start = clean_sprint_datetime(sprint.startDate)
    sprint_end = clean_sprint_datetime(sprint.endDate)
    
    for issue, details in issues.items():
        if issue not in issue_facts:
            issue_facts[issue] = {}
              
        for name, sprint_fact in SPRINT_FACTS.items(): 
            if name not in sprint_facts:
                sprint_facts[name] = 0
            
            result = sprint_fact(issue, details, sprint_start, sprint_end, sprint)
            sprint_facts[name] += result
            
        for name, issue_fact in ISSUE_FACTS.items():
            fact_results = issue_fact(issue, details)
            if fact_results is not None: 
                issue_facts[issue][name] = fact_results
                                
    return sprint_facts, issue_facts


def get_facts(issues, sprint):    
    return get_issue_facts(issues, sprint)
    
def get_issue_totals(sprints): 
    issue_totals = {}
    # build unique issue set - there must be a better way of doing this!
    all_issues = {
        issue_name:issue_details for sprint_name, sprint_details in sprints.items() 
        for issue_name, issue_details in sprint_details["issues"].items()
    }
    unique_issue_names = (name for name, details in all_issues.items())
    
    unique_issues = [
        all_issues[name] for name in unique_issue_names
    ]
    
    # pass issues to fact
    for name, fact in ISSUE_TOTALS.items(): 
        issue_totals[name] = fact(unique_issues)
    
    return issue_totals
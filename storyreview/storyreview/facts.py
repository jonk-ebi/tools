from datetime import datetime, timedelta

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

ISSUE_FACTS = {} # Holds dictionary of issue fact functions, populated by is_fact
SPRINT_FACTS = {} 
POST_PROCESS_FACTS = {}

PADDING_DELTA = timedelta(hours = 23)

def is_issue_fact(fact): 
    ISSUE_FACTS[fact.__name__] = fact
    return fact

def is_sprint_fact(fact): 
    SPRINT_FACTS[fact.__name__] = fact
    return fact

def is_post_process_fact(fact): 
    POST_PROCESS_FACTS[fact.__name__] = fact
    return fact
          
def clean_sprint_datetime(sprint_date): 
    return datetime.fromisoformat(sprint_date[:sprint_date.rfind(".")])
          
@is_issue_fact
def issue_life_span(issue, issue_details, event, change): 
    if change["field"] == "status" and change["toString"].lower() in FINISHED_STATUSES:
        #Calculate delta
        created_date = datetime.fromisoformat(issue_details['created'])
        closed_date = datetime.fromisoformat(event['occured'])
        #print(f"Issue {issue} life span {closed_date - created_date}")
        return (closed_date - created_date).days
    return None

@is_issue_fact
def issue_end_status(issue, issue_details, event, change): 
    if change["field"] == "status" and change["toString"].lower() in FINISHED_STATUSES:
        return change["toString"].lower()
    return None
    
@is_issue_fact
def issue_number_of_sprints(issue, issue_details, event, change): 
    if change["field"].lower() == "sprint": 
        return change["toString"].split(',')
    return None

@is_sprint_fact
def sprint_issues_cancelled(issue, issue_details, event, change, sprint_start, sprint_end, sprint):
    if change["field"] == "status" and change["toString"].lower() == CANCELLED_STATE: 
        cancelled_date = datetime.fromisoformat(event['occured'])
        if cancelled_date >= sprint_start: 
            return 1
    return 0

@is_sprint_fact
def sprint_starting_issue_count(issue, issue_details, event, change, sprint_start, sprint_end, sprint):
    if change["field"].lower() == "sprint" and sprint.name in change["toString"]:
        add_to_sprint_date = datetime.fromisoformat(event['occured'])
        #print(f"Added to sprint {add_to_sprint_date - sprint_start}")
        delta = add_to_sprint_date - sprint_start
        if delta <= PADDING_DELTA: 
            return 1
    return 0
    
@is_sprint_fact
def sprint_total_issues_count(issue, issue_details, event, change, sprint_start, sprint_end, sprint):
    if change["field"].lower() == "sprint" and sprint.name in change["toString"]:
        return 1
    return 0
    
@is_sprint_fact
def sprint_issues_added_after_count(issue, issue_details, event, change, sprint_start, sprint_end, sprint):
    if change["field"].lower() == "sprint" and sprint.name in change["toString"]:
        add_to_sprint_date = datetime.fromisoformat(event['occured'])
        #print(f"Added to sprint {add_to_sprint_date - sprint_start}")
        delta = add_to_sprint_date - sprint_start
        if delta > PADDING_DELTA: 
            return 1
    return 0

@is_sprint_fact
def sprint_issue_count_at_end_of_sprint(issue, issue_details, event, change, sprint_start, sprint_end, sprint):
    if change["field"].lower() == "sprint" and sprint.name in change["toString"]:
        # check if done
        if issue_details["status"] in FINISHED_STATUSES:
            return 1
        else: 
            for other_event in issue_details["events"]:
                for other_change in other_event["changes"]:
                    if other_change["field"] == "status" and change["toString"].lower() in FINISHED_STATUSES:
                        date_issue_was_done = datetime.fromisoformat(other_change['occured'])
                        if date_issue_was_done > sprint_end: 
                            return 1
                        
    return 0

@is_post_process_fact
def shrink_issue_number_of_sprints(issue_facts, sprint_facts): 
    for issue, facts in issue_facts.items(): 
        target = issue_number_of_sprints.__name__
        list_of_sprints = {sprint.strip() for event in facts[target] for sprint in event if len(sprint) > 0}
        if len(list_of_sprints) > 0: 
            #print(issue,list_of_sprints)
            facts[target] = len(list_of_sprints)
        else: 
            facts[target] = 1 # if an issue is assigned a sprint on creation it is not included in it's history

@is_post_process_fact 
def shrink_issue_life_span(issue_facts, sprint_facts): 
    for issue, facts in issue_facts.items(): 
        target = issue_life_span.__name__
        if len(facts[target]) > 0: 
            facts[target] = facts[target][0]
        else: 
            facts[target] = -1
            
@is_post_process_fact 
def clean_issue_end_status(issue_facts, sprint_facts): 
    for issue, facts in issue_facts.items(): 
        target = issue_end_status.__name__
        if len(facts[target]) > 0: 
            facts[target] = facts[target][0]
        else: 
            facts[target] = ""

def get_issue_facts(issues, sprint):
    issue_facts = {}
    sprint_facts = {}
    #HACK: this is really ugly
    sprint_start = clean_sprint_datetime(sprint.startDate)
    sprint_end = clean_sprint_datetime(sprint.endDate)
    
    for issue, details in issues.items():
        if issue not in issue_facts:
            issue_facts[issue] = {}
              
        for name, sprint_fact in SPRINT_FACTS.items(): 
            if name not in sprint_facts:
                sprint_facts[name] = 0
            for event in details["events"]:
                for change in event["changes"]: 
                    sprint_facts[name] += sprint_fact(issue, details, event, change, sprint_start, sprint_end, sprint)
            
        for name, issue_fact in ISSUE_FACTS.items():
            if name not in issue_facts[issue]: 
                issue_facts[issue][name] = []
            for event in details["events"]:
                for change in event["changes"]: 
                    fact_results = issue_fact(issue, details, event, change)
                    if fact_results is not None: 
                        issue_facts[issue][name].append(fact_results)  
                          
    for name, process_fact in POST_PROCESS_FACTS.items():
        process_fact(issue_facts, sprint_facts)         
    return sprint_facts, issue_facts


def get_facts(issues, sprint):    
    return get_issue_facts(issues, sprint)
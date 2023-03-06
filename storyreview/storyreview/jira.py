import sys
from datetime import datetime, timedelta
from jira import JIRA

FIELDS_OF_INTREST = ["sprint","status","description", "resolution"]
FIELD_SPRINT = FIELDS_OF_INTREST[0]
FIELD_STATUS = FIELDS_OF_INTREST[1]

SPRINT_END_CORRECTION_DELTA = timedelta(minutes=-1)

def explore_issue(issue):
    print(issue.fields.summary)
    for property, value in vars(h).items():
        if property == "items": 
            continue
        print(f"{property}: {value}")
    for item in h.items:
       for property, value in vars(item).items():
           print(f"\t{property}: {value}") 

def iso_datetime_without_timezone(date): 
    return date[:date.rfind("+")]
    
def get_issue_history(issue, sprint):
    """Used to collect useful facts from the Jira issue object """     
    # for sprint movement check if movement happened in sprint time
    issue_summary = {}
    issue_summary['id'] = issue.id
    issue_summary['title'] = issue.key
    issue_summary['created'] = iso_datetime_without_timezone(issue.fields.created)
    issue_summary['status'] = str(issue.fields.status).lower()
    #issue_summary['resolved'] = issue.fields.resolved
    events = []

    for history in issue.changelog.histories:
        event = {}
        event['occured'] = iso_datetime_without_timezone(history.created) 
        event['author'] = history.author.key
        event['author_name'] = history.author.displayName
        event['changes'] = []
        
        #if len(history.items) > 0: 
        #    print(f"Multiple items for a single event for {issue_summary['title']}")
        is_of_interest = False
        for item in history.items:
            low_field = item.field.lower()
            if low_field in FIELDS_OF_INTREST:
                #print(f"Field {low_field} found for {issue.key}")
                #print(f"-- To {str(item.toString).lower()}")
                is_of_interest = True
                change = {}
                change['field'] = low_field
                change['fromString'] = str(item.fromString).lower()
                change['toString'] = str(item.toString).lower()
                event['changes'].append(change)
                
        if is_of_interest:
            events.append(event)
       
    # Change to ensure that all issues have a sprint linked to them. 
    # If a issue has a sprint linked to it during creation then that sprint does not show in the history
    event = {
        'occured': issue_summary['created'],
        'author': -1,
        'author_name': "Added",
        'changes':[
            {
                'field':FIELD_SPRINT,
                'fromString':"",
                'toString':sprint.name,
            },
            {
                'field':FIELD_STATUS,
                'fromString':"",
                'toString':"To Do",
            },
        ],
    }
    events.append(event)
   
    issue_summary['events'] = events;
    return issue_summary

def __clean_sprint_date(sprint_date): 
    return datetime.fromisoformat(sprint_date[:sprint_date.rfind(".")]) 
    
def get_sprints(url, token, board, offset=0): 
    jira = JIRA(
        server=url,
        token_auth=token
    )
    sprints = []

    while True:
        new_sprints = jira.sprints(
                board_id = int(board),
                startAt = offset,
                maxResults = 50
            )
        if len(new_sprints) == 0:
            break
        
        offset += len(new_sprints)
        sprints.extend(new_sprints)
        
    #Prevent sprints overlapping
    for x in range(0,len(sprints) -1):
        if sprints[x].state != "closed":
            continue
        
        currentSprintEnd = __clean_sprint_date(sprints[x].endDate)
        nextSprintStart = __clean_sprint_date(sprints[x + 1].startDate)
        if currentSprintEnd > nextSprintStart: 
            print(f"Altering end date for sprint f{sprints[x].name}")
            print(sprints[x].endDate)
            #Another horrible hack!
            sprints[x].endDate = (nextSprintStart - SPRINT_END_CORRECTION_DELTA).isoformat() + ".000Z"
    
    return sprints
    
def collapse_issue_history_into_snapshot(start_time, end_time, issue): 
    """"for each history event type it try to find the last thing that happened within the sprint window"""
    snapshots = {
        'common': { 
            'id': issue['id'],
            'title': issue['title'],
            'created': issue['created'],
        }
    }
    
    for event in issue["events"]: 
        
        if event['occured'] >= end_time: 
            continue
            
        for change in event["changes"]:     
            update_status = False
            if change['field'] not in snapshots:
                update_status = True
            elif event['occured'] > snapshots[change['field']]['occured']:
                update_status = True
            
            if update_status:
                snapshots[change['field']] = {
                    'occured': event['occured'],
                    'change':change['field'],
                    'value':change['toString'],
                }
    return snapshots     
    

def get_sprint_details(url, token, sprint): 
    jira = JIRA(
        server=url,
        token_auth=token
    )

    print(f"Target sprint {sprint.name}")
    print(f"From {sprint.startDate} to {sprint.endDate}")
    issues = jira.search_issues(f"sprint={sprint.id}")
    
    #Gather issue details <- this needs to move to a function so it can be used on all sprints
    issue_details = {}
    issue_snapshots = {}
    for issue_holder in issues:
        issue = jira.issue(issue_holder.id, expand='changelog')
        issue_details[issue.key] = get_issue_history(issue, sprint)
        issue_snapshots[issue.key] = collapse_issue_history_into_snapshot(
            sprint.startDate, 
            sprint.endDate, 
            issue_details[issue.key]
        )
     
    return issue_details, issue_snapshots
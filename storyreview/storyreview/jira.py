from jira import JIRA

FIELDS_OF_INTREST = ["sprint","status","description", "resolution"]

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
    
def get_issue_history(issue):
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
        #From history
        #- created
        #- author
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
                is_of_interest = True
                change = {}
                change['field'] = low_field
                change['fromString'] = item.fromString
                change['toString'] = item.toString
                event['changes'].append(change)
                
        if is_of_interest:
            events.append(event)
        
    issue_summary['events'] = events;
    return issue_summary

def get_sprint_details(url, token, board): 
    jira = JIRA(
        server=url,
        token_auth=token
    )
    
    #project = jira.project(cli.project)
    #print(f"Connected to {project.name}")

    # TODO need to add paging here
    sprints = jira.sprints(
        board_id = int(board),
        startAt = 51,
        maxResults = 50
    ) # Look at how to order
    
    print(f"Latest sprint is {sprints[-1].name} with status {sprints[-1].state}")
    
    #for sprint in sprints:
    #    print(sprint.name)
    print(f"Sprints found:{len(sprints)}")
    target = -3
    print(f"Target sprint {sprints[target].name}")
    print(f"From {sprints[target].startDate} to {sprints[target].endDate}")
    issues = jira.search_issues(f"sprint={sprints[target].id}")
    
    #Gather issue details <- this needs to move to a function so it can be used on all sprints
    issue_details = {}
    for issue_holder in issues:
        issue = jira.issue(issue_holder.id, expand='changelog')
        issue_details[issue.key] = get_issue_history(issue)
    return issue_details, sprints[target]
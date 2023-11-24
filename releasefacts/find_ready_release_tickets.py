import sys
from argparse import ArgumentParser
from jira import JIRA

JIRA_URL = "https://www.ebi.ac.uk/panda/jira"
FIXVERSION = "Ensembl"
FIXVERSION_FORMAT = "Ensembl {}"
REQUIRES_LINKTYPES = ["After","Required"]
RESOLVED_STATUS = ["Done","Resolved"]

def getCLICommands(): 
    parser = ArgumentParser(
        description="A little tool used to discover release tickets that are ready to be worked on",
        usage=f"python {sys.argv[0]} -t TOKEN"
    )
     
    parser.add_argument(
        "-t",
        "--token",
        required=True,
        help = "API token"
    )
    
    parser.add_argument(
        "-r",
        "--release",
        required=True,
        help="Release version - \"Ensembl 111\" or 111"
    )
    
    parser.add_argument(
        "-j",
        "--host",
        default = JIRA_URL, 
        help = f"Jira host - defaults to {JIRA_URL}"
    )
    
    return parser


def get_jira_connection(host, token):
    return JIRA(
        server=host,
        token_auth=token
    )
   
     
def collect_reopened_tickets(conn, release): 
    query = f"project = ENSWEBREL AND status = Reopened AND fixVersion in ('{release}') ORDER BY priority DESC, updated DESC"
    
    #loop through collecting 
    issues = []
    offset = 0
    request_count = 25
    while results := conn.search_issues(jql_str=query,startAt=offset,maxResults=request_count): 
        offset += request_count
        issues.extend(results)
        
    print(f"{len(issues)} tickets remaining for release {release}")
    return issues
    
def get_required_issues(issues): 
    required = []
    for i in issues:
        required.extend([
            l.outwardIssue for l in i.fields.issuelinks 
            if "outwardIssue" in l.raw and l.type.name in REQUIRES_LINKTYPES
        ]) 
    return required
                
def group_by_components(issues): 
    group = {} 
    
    for i in issues: 
        for c in i.fields.components:
            if c.name not in group:
                group[c.name] = []
            group[c.name].append(i)
    return group
                
def find_ready_release_tickets(host, token, release, update): 

    if FIXVERSION not in release:
        release = FIXVERSION_FORMAT.format(release)
        
    jira_conn = get_jira_connection(host, token)
        
    print(f"Lets go for {release}!")
    print("Will update ready tickets!" if update else "Dry run")
    
    #print(jira_conn.issue_link_types())
    #return
    #print([f"{k['id']}={k['name']}" for k in jira_conn.fields() if "comp" in k['name'].lower()])
    

    issues = collect_reopened_tickets(jira_conn, release)
    ready_tickets = []
    top_level_tickets = []
    
    for test in issues:
    
        if len(test.fields.issuelinks):
            required_issues = get_required_issues([test])
            
            if len(required_issues) > 0:
                outstanding_issues = [
                    issue for issue in required_issues 
                    if issue.fields.status.name not in RESOLVED_STATUS
                ]
                is_ticket_ready = len(outstanding_issues) == 0

                if is_ticket_ready: 
                    ready_tickets.append(test)
                else:
                    print(f"{test.key} has {len(outstanding_issues)} outstanding tickets")
            else: 
                #print(f"Top level ticket {test.key} is still open")
                ready_tickets.append(test)
                top_level_tickets.append(test.key)
                
    print("")           
    if len(ready_tickets) > 0:
        
        grouped_tickets = group_by_components(ready_tickets)
        ordered_groups = [k for k in grouped_tickets.keys()]
        ordered_groups.sort()
        
        print("Ready tickets")
        for name in ordered_groups:
            print(f"Component {name}")
            group = grouped_tickets[name]
            for i in group:
                top = "Top level." if i.key in top_level_tickets else ""
                print(f"{top}{i.key} - {i.fields.summary}")
            print(" ")
        print(f"{len(ready_tickets)}/{len(issues)} tickets are ready for {release}")
    else: 
        print("No new tickets ready :D")
    
def find_ready_release_tickets_cli(args): 
    cli = getCLICommands().parse_args(args)
    find_ready_release_tickets(cli.host, cli.token, cli.release, False)
     
           
if __name__ == "__main__": 
    find_ready_release_tickets_cli(sys.argv[1:])
import sys
import os
import json
from argparse import ArgumentParser

from storyreview.jira import get_sprints, get_sprint_details
from storyreview.facts import get_facts, get_issue_averages

# poetry run python -m storyreview -t  -b 332
# need to add config for jira URL?

JIRA_URL = "https://www.ebi.ac.uk/panda/jira"

def getCLICommands(): 
    parser = ArgumentParser(
        description="Story Review - gathers metrics for stories linked to sprints within a Jira project"
    )
    
    parser.add_argument(
        "-b",
        "--board",
        help="Jira board id"
    )
    
    parser.add_argument(
        "-t",
        "--token",
        help = "API token"
    )
    
    parser.add_argument(
        "-j",
        "--host",
        default = JIRA_URL, 
        help = "Jira host"
    )
    
    return parser

def story(args): 
    cli = getCLICommands().parse_args(args)
    
    print("Story review")
    print(f"Connecting to {JIRA_URL}")
    
    # get sprints
    sprints = get_sprints(cli.host, cli.token, cli.board)
    print(f"Sprints found: {len(sprints)}")
    print(f"Latest sprint is {sprints[-1].name} with status {sprints[-1].state}")
    #for sprint in sprints: 
    #    print(sprint.name)
    
    # compile facts
    facts = {}
    for sprint in sprints[-4:]:
        if sprint.state != "future":
            issue_details = get_sprint_details(cli.host, cli.token, sprint)
            sprint_facts, issue_facts = get_facts(issue_details, sprint) 
            facts[sprint.name] = {
                "issues":issue_facts,
                "sprint":sprint_facts
            }
    
    facts['issue_averages'] = get_issue_averages(facts)
      
    # output json
    with open("beta_sprints.json","w") as report:
        report.write(json.dumps(facts, indent=4))
    
        
if __name__ == "__main__": 
    story(sys.argv[1:])
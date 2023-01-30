import sys
import os
from argparse import ArgumentParser

from storyreview.jira import get_sprint_details
from storyreview.facts import get_facts

# poetry run python -m storyreview -t TOKEN -b 332
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
    
    issue_details, sprint = get_sprint_details(cli.host, cli.token, cli.board)
    sprint_facts, issue_facts = get_facts(issue_details, sprint) 
    print(issue_facts)
        
if __name__ == "__main__": 
    story(sys.argv[1:])
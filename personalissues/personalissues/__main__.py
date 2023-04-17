import sys 

from personalissues.personal_issues import personal_issues_cli

if __name__ == "__main__": 
    personal_issues_cli(sys.argv[1:])
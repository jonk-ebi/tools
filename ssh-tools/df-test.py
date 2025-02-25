import subprocess
import sys
import json


def process_output(output: str, targets) -> None:

    lines = output.splitlines()
    found = 0
    possible_errors = []
    for line in lines:
        columns = [c.strip() for c in line.split(' ') if len(c) > 0]
        for target, expected in targets.items(): 
            if columns[0] == target:
                if columns[-1] == expected:
                    found += 1
                else:
                    possible_errors.append(
                        f"\tError: {targets} -> {columns[-1]}. Expected {expected}"
                    )
    if found >= len(targets):
        print("\tLooks good")
    else:
        if len(possible_errors) > 0:
            for p in possible_errors:
                print(p)
        else:
            print("\tNo mapping found!")


def scan_hosts(hosts, targets):
    command = "df -Pkh"

    for host in hosts:
        print(f"Connecting to {host}")
        ssh_command = f"ssh -o 'StrictHostKeyChecking=No' {host} '{command}'"
        process = subprocess.Popen(
            ssh_command,
            shell=True,
            stdout=subprocess.PIPE
        )
        output, error = process.communicate()
        if error and len(error) > 0 or len(output) == 0:
            print("\tConnection error")
        else:
            process_output(output.decode("utf-8"), targets)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        with open(sys.argv[2]) as targets_file:
            targets = json.load(targets_file)
        
        with open(sys.argv[1]) as host_file:
            hosts = host_file.read().splitlines()
            print(f"Testing {len(hosts)} hosts")
            scan_hosts(hosts, targets)
    else:
        print(f"Expected: {sys.argv[0]} hosts.txt targets.json")
        print("host.txt: A line delimited list of host names to check")
        print("targets.json: A dictionary of targets and expected mapping")
        print("""{\n\t"my-host:/my/nfs/path":"/nfs/my/mount"\n}""")

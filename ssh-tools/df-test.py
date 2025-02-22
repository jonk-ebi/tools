import subprocess
import sys


def process_output(output: str) -> None:

    targets = [
        "hh-isi-srv:/ifs/public/ro/ensweb_codon",
        "hh-isi-srv:/ifs/public/ro/ensweb-data_codon",
        "hh-isi-srv:/ifs/public/ro/ensweb-software_codon",
    ]

    expected = [
        "/nfs/public/ro/ensweb",
        "/nfs/public/ro/ensweb-data",
        "/nfs/public/ro/ensweb-software",
    ]

    lines = output.splitlines()
    found = 0
    possible_errors = []
    for line in lines:
        columns = [c.strip() for c in line.split(' ') if len(c) > 0]
        for i in range(0, len(targets)):
            if columns[0] == targets[i]:
                if columns[-1] == expected[i]:
                    found += 1
                else:
                    possible_errors.append(
                        f"\tError: {targets[i]} -> {columns[-1]}. Expected {expected[i]}"
                    )
    if found >= len(targets):
        print("\tLooks good")
    else:
        if len(possible_errors) > 0:
            for p in possible_errors:
                print(p)
        else:
            print("\tNo Codon mapping found!")


def scan_hosts(hosts):
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
            process_output(output.decode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        with open(sys.argv[1]) as host_file:
            hosts = host_file.read().splitlines()
            print(f"Testing {len(hosts)} hosts")
            scan_hosts(hosts)
    else:
        print("Missing line delimited file of host names")

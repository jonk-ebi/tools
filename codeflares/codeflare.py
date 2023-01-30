import sys
import os
import argparse
import re

from pathlib import Path

DESCRIPTION = "A tool for pulling out comments from a code base, based on specific key words"

SINGLE_LINE = re.compile("\/\/[\x20-\x7E\t]+\n")
#MULTI_LINE  = re.compile("\/\*[^\*]+")
MULTI_LINE  = re.compile("/\*[^*]*\*+(?:[^/*][^*]*\*+)*/")

FLARES = [
    "todo",
    "hack",
    "fixme",
    "bug"
]

TARGET_SUFFIX = [".ts", ".tsx"]

def getCLIArguments(): 
    cli = argparse.ArgumentParser(
        prog='Code Flares',
        description=DESCRIPTION,
    )
    
    cli.add_argument(
        'folder',
        help='root folder of code base you want to scan'
    )
    return cli
    
def scanFolderTree(folder): 
    rootPath = Path(folder)
    files = list(p.resolve() for p in rootPath.glob("**/*") if p.suffix in TARGET_SUFFIX)
    return files
    
def firstWord(flare): 
    word = ""
    wordBits =  flare[2:].strip().split(" ")
    for wordIndex in range(0,3):
        testWord = wordBits[wordIndex].replace('*','').strip()
        if len(testWord) > 0:
            word = testWord
            break

    if word.endswith(":"): 
        return word[:-1]
    else: 
        return word

def getLineNumber(target, source):
    if "\n" in target:
        target = target.split("\n")[0]
    
    if "\n" not in source:
        return 1
    
    sourceLines = source.split("\n")
    for line in range(0, len(sourceLines)): 
        if target in sourceLines[line]: 
            return line + 1
    return -1

def scanString(regex, sourceCode):  
    hits = regex.findall(sourceCode)
    
    comments = len(hits)

    flares = [flare for flare in hits if firstWord(flare).lower() in FLARES]
    lines = [getLineNumber(flare, sourceCode) for flare in flares]
    #TODO we need line numbers 
    return flares, lines, comments

def codeFlare(folder):
    print("## Quick code scanner")
    print(f"**Scanning:** {folder}")
    
    # build file list
    files = scanFolderTree(folder)
    
    print(f"**Files:** {len(files)}")

    results = {}
    for file in files:
        with open(file,"r") as fileReader:
            fileContents = fileReader.read()
            
            flares = []
            lines = []
            comments = 0
            # scan for single line comments
            f, l, c = scanString(SINGLE_LINE, fileContents)
            flares.extend(f)
            lines.extend(l)
            comments += c
            #scan for multi line comments
            f, l, c = scanString(MULTI_LINE, fileContents)
            flares.extend(f)
            lines.extend(l)
            comments += c
            results[file] = {"flares":flares,"lines":lines, "comments": comments}
        
    for file, result in results.items():
        if len(result['flares']) == 0: 
            continue 
        print("------------")
        print(f"**File:** {file}")
        print(f"**Flares:** {len(result['flares'])}\n**Comments:** {result['comments']}")
        lineCounter = 0
        for f in result['flares']:
            print("")
            print(f"**Starting at line:** {result['lines'][lineCounter]}")
            print(f"```typescript\n{f}```")
            lineCounter += 1
    
    
    
def exeCodeFlare(args):
    cli = getCLIArguments()
    cliArguments = cli.parse_args(args)
    
    if os.path.isdir(cliArguments.folder):
        codeFlare(cliArguments.folder)
    else:   
        print(f"'{cliArguments.folder}' is not a directory")
     
if __name__ == "__main__": 
    exeCodeFlare(sys.argv[1:])
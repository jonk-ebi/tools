## cbor2-decomp

A set of tools for viewing CBOR2 encoded files and HTTP requests

**cbor2-decomp.py**: Takes in a CBOR2 encoded file and outputs JSON - can be used to decompile EARDO files
**Usage**: `python cbor2-decomp.py [FILE PATH] [OUTPUT FILE PATH]`
**Example**: `poetry run python cbor2-decomp.py render16.eardo render16.json`

**-har-cbor2-decomp.py**: Given a har file returns a json object containing any genome browser backend requests with CBOR2 values converted to JSON
**Usage**: `python har-cbor2-decomp.py [FILE PATH] [OUTPUT FILE PATH]`
**Example**: `poetry run python har-cbor2-decomp.py gb_usage.har gb_usage.json`
**Notes**: You can get a har file via your browser developer tools 

## Install

1. git clone
2. cd personalissues
3. poetry install
4. poetry run python cbor2-decomp.py **or** poetry run python har-cbor2-decomp.py

## Notice

- Tools are very bare bones and make a bunch of assumptions.
- All tools convert binary strings into a string of base 10 bytes e.g. `128, 26, 255, 0`
- **har-cbor2-decomp.py** currently filters har entries request urls by `api/browser/data`
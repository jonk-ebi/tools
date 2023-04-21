import sys
import json
import base64

from collections.abc import Mapping, Set

import cbor2

KNOWN_GOOD_TYPES = [str, bool, int, float]

def byte_to_string(bytes):
    return ", ".join(map(lambda b: str(b) ,bytes))
            
def tag_hook(decoder, tag):
    print(tag)
    return str(tag)
    
def handle_list(obj):
    obj_list = []
    for i in obj:
        obj_list.append(handle_obj(i))
    return obj_list
    
def handle_dict(obj):
    keys = list(obj.keys())
    for key in keys:
        obj[key] = handle_obj(obj[key])
    return obj
    
def handle_obj(obj):
    if isinstance(obj, Mapping):
        return handle_dict(obj)
    elif type(obj) is list:
        return handle_list(obj)
    elif type(obj) is bytes:
        return byte_to_string(obj)

    if type(obj) not in KNOWN_GOOD_TYPES:
        print(f"Handle obj defaulted for unexpected type {type(obj)}")
    return obj

def object_hook(decoder, obj):
    return handle_obj(obj)
  
def decompile_cbor2(cbor2_str): 
    return cbor2.loads(cbor2_str,tag_hook=tag_hook, object_hook=object_hook)
    
def process_har(har_path, output, target_url ):
    with open(har_path) as har_stream:
        har = json.load(har_stream)

    logs = har["log"]
        
    HAR_ENTRIES = "entries"
    if HAR_ENTRIES not in logs:
        print(f"Unable to find {HAR_ENTRIES}")
        return
    
    print(f"Scanning {len(logs[HAR_ENTRIES])} requests")
    
    cbor2_requests = []
    
    for entry in logs[HAR_ENTRIES]:
        if target_url in entry["request"]["url"]:
            new_request = {}
            new_request['url'] = entry["request"]["url"]
            sent = entry["request"]["postData"]["text"]
            got = entry["response"]["content"]["text"]
            new_request['sent'] = decompile_cbor2(sent.encode('raw_unicode_escape'))
            new_request['got'] = decompile_cbor2(base64.b64decode(got))
            json.dumps(new_request['got'])
            cbor2_requests.append(new_request)
    
    print(f"Found {len(cbor2_requests)} for {target_url}")
    with open(output,'w') as out_stream:
        out_stream.write(json.dumps(cbor2_requests, indent=4))

if __name__ == "__main__": 
    target_url = "api/browser/data"
    process_har(sys.argv[1],sys.argv[2],target_url)
import sys
import json

from collections.abc import Mapping

import cbor2

def byte_to_string(bytes):
    return ", ".join(map(lambda b: str(b) ,bytes))
    
def scan_list(slist):
    for i in slist:
        if type(i) is list:
            scan_list(i)
        elif type(i) is bytes:
            i = byte_to_string(i)
            
def tag_hook(decoder, tag):
    print(tag)
    return str(tag)

def object_hook(decoder, obj):
    #print(type(value))
    if isinstance(obj, Mapping):
        print("IS DICT!!")
        keys = list(obj.keys())
        for key in keys:
            if type(obj[key]) is bytes:
                obj[key] = byte_to_string(obj[key])
        return obj
    return str(obj)
    

def decompile_cbor2(path, output): 
    with open(path, 'rb') as f: 
        raw = f.read()
        cbor2_data = cbor2.loads(raw,tag_hook=tag_hook, object_hook=object_hook)
    
     
    with open(output,"w") as dump: 
        dump.write(json.dumps(cbor2_data, indent=4))

if __name__ == "__main__": 
    decompile_cbor2(sys.argv[1],sys.argv[2])
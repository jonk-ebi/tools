import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

SOP_MISSING = "missing"
JIRA = "https://www.ebi.ac.uk/panda/jira/browse/"

def get_config(path = "config.json"):
    with open(path) as config_raw:
        config = json.load(config_raw)
    
    #expand config
    expanded_vms = {}
    for vm,details in config["vms"].items():
        if "[" in vm:
            start = vm.find('[') 
            end = vm.find(']')
            prefix = vm[0:start]
            range = vm[start + 1:end]
            for v in range:
                expanded_vms[f"{prefix}{v}"] = details
        else:
            expanded_vms[vm] = details
    config["vms"] = expanded_vms
    return config
    

def generate_data():
    OH_URL = "http://useast.ensembl.org:8000/oh.html"
    NO_CONNECTION_ERROR = "==> Could not connect <=="
    
    config = get_config()
    
    r = requests.get(OH_URL)
    if r.status_code != 200: 
        return (False,"Unable to access oh!")
        
    oh = BeautifulSoup(r.text, 'html.parser') 
    #get pre and get all child spans
    spans = oh.pre.find_all("span")
    blob = ""
    for span in spans: 
        if span.string:
            blob += span.string
    
    #find column sizes
    lines = blob.splitlines()
    column_sizes = [len(c) for c in lines[2].split(' ') if len(c) > 0]
    
    index = 0
    columns = []
    data = []
    for s in column_sizes:
        columns.append(
            f"{lines[0][index:index + s].strip()}{lines[1][index:index + s].strip()}"
        )

        index += s + 1

    has_no_connection_error = False
    for line in lines[3:]:
        row = {}
        index = 0
        if len(line.strip()) == 0:
            break
        
        if NO_CONNECTION_ERROR in line: 
            data.append({
                f"{columns[0]}":line[0:column_sizes[0]].strip(),
                "could not connect":"ALARM!"
            })
            has_no_connection_error = True
        else:
            for x in range(len(column_sizes)):  
                if(len(line)>= index + s):
                    row[columns[x]] = line[index:index + s].strip()
                index += column_sizes[x] + 1
            data.append(row)
            
    # organise table
    errors = columns[1:]
    if has_no_connection_error: 
        errors.append("could not connect")
    
    host_column = columns[0]
    report = {}
    
    ignore_msgs = ["Ok",""]
    
    for row in data:
        vm = row[host_column]
        if vm in config["vms"]:
            service = config["vms"][vm]["service"]
            site = config["vms"][vm]["site"]
        else: 
            service = ""
            site = ""
        
        report[vm] = {
            'errors':[{"error":err,"output":msg} for err, msg in row.items() 
                if err in errors and msg not in ignore_msgs
            ],
            'info': {
                "service":service, 
                "site":site
            }
        }
    
    #enrich errors 
    for vm, d in report.items(): 
        service = d['info']['service']
        if "-fallback" in service:
            service = service.split('-')[0]
        for e in d["errors"]: 
            if service in config['sops']:
                if e["error"] in config["sops"][service]: 
                    e["sop"] = config["sops"][service][e["error"]]
                elif e['error'] in config['generic_sops']:
                    e["sop"] = config["generic_sops"][e["error"]]
                else:
                    e['sop'] = SOP_MISSING
            else:
                if e["error"] in config['generic_sops']:
                    e["sop"] = config["generic_sops"][e["error"]]
                else:
                    e['sop'] = SOP_MISSING

    return (True,report)
     
def link_if_sop(alert, sop):
    if sop == SOP_MISSING:
        return alert
    return f"<a href='{JIRA}{sop}'>{alert}</a>"
     
#----------------------------------     
#Setup streamlit
st.set_page_config(page_title="Oh nice!", page_icon=":chart_with_upwards_trend:", layout="wide")

data = generate_data()

st.markdown("# Oh Nice!")

if data[0]:
    #st.dataframe(data[1])
    report = data[1]
    
    st.markdown("## Summary")
    st.markdown(f"**VMs with issues:** {len(report)}")
    
    error_count = sum(
        [len(d['errors']) for _, d in report.items()]
    )
    
    st.markdown(f"**Total alerts:** {error_count}")
    
    summary = [
        { 
            'host':f"<a href='#{vm}'>{vm}</a>", 
            'service':d['info']['service'],
            'site':d['info']['site'],
            'alerts':", ".join([link_if_sop(e['error'],e['sop']) for e in d['errors']])
        }
        for vm,d in report.items()
    ]
    
    df = pd.DataFrame(summary, columns = summary[0].keys())
    st.markdown(df.style.to_html(),unsafe_allow_html=True)
    
    st.markdown("## Alerts")
    
    for host, details in report.items():
        if details['info']['service']:
            st.markdown(f"### {host}")
            st.markdown(f"**{details['info']['service']} {details['info']['site']}**")
        else: 
            st.markdown(f"### {host}")
        st.markdown("**Alerts**")
        
        errors = details['errors'].copy()
        
        for e in errors:
            sop = e['sop']
            if sop != SOP_MISSING: 
                e["sop"] = f"<a href='{JIRA}{sop}'>{sop}</a>"
        
        df = pd.DataFrame(errors, columns = details["errors"][0].keys())
        st.markdown(df.style.to_html(), unsafe_allow_html=True)
        
    
    
    #st.markdown(data[1].style.to_html(), unsafe_allow_html=True)
else:
    st.write(f"Error building view: {data[1]}")
    



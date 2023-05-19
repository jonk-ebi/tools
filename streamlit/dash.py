import toml

import streamlit as st
import pandas as pd

from data import JiraData

# TODO
# - factor in project people 
# - improve summary tables - highlights and index
# - add project links
# - add a new issues section to summary
# - add a my issues tab
# - days since assigned 

# - project specfic 

def load_settings(toml_path):
    
    with open(toml_path) as toml_stream:
        return toml.load(toml_stream)
        

def update_all_projects(projct_list, team_list, token):

    for project in projct_list: 
        d.update_data(project, team_list, token)
        
def reset_deltas():
    d.save_data() 
    
        
config = load_settings("settings.toml")
project_list = config['settings']['projects']
d = JiraData(project_list)

team_list = config['settings']['team']
project_settings = {project:config[project] for project in project_list}

project_name_list = [f"{p} ({project_settings[p]['name']})" for p in project_list]

#-- Setup dashboard 
st.set_page_config(page_title="Ensembl Jira Dash", page_icon=":chart_with_upwards_trend:", layout="wide")

st.markdown("""
<style>
     div[data-testid="metric-container"]
     {
         height:4em;
     }
     
     div[data-testid="stMetricValue"]
     {
        width:3em;
        display:inline-block; 
     }
     
     div[data-testid="stMetricDelta"]
     {
         position:relative;
         top:-2.5em; 
         left:3em;
     }
     
     div[data-testid="stMetricDelta"] div
     {
         display:inline
     }
     
     
</style>
"""
,unsafe_allow_html=True)

#-- Build dashboard

st.button("Refresh Data", on_click=update_all_projects, args=[project_list, team_list, config['jira']['token']], type="primary")
st.button("Reset Deltas", on_click=reset_deltas, type="primary")

tab_names = ["Summary"]
tab_names.extend(project_name_list)

tabs = st.tabs(tab_names)
summary_tab = tabs[0]
project_tabs = tabs[1:]

# Summary ----
with summary_tab:
    columns = st.columns(2)
    col_index = 0
    
for x in range(0,len(project_list)):
    project = project_list[x]
    project_name = project_name_list[x]
    df = d.build_personal_load(project)
    with columns[col_index]:
        st.write(f"{project_name} tickets")
        st.dataframe(df.style.background_gradient(cmap="Blues", vmin=0, vmax=100), use_container_width=True)
    col_index += 1
    if col_index >= len(columns):
        col_index = 0

# Project details ----
for x in range(0,len(project_tabs)):
    project = project_list[x]
    project_name = project_name_list[x]
    with project_tabs[x]:
        df = d.build_issues(project)
        st.write(f"{project_name} Issue board")
        st.markdown(df.style.bar(subset=['life'], color='#d65f5f').hide(axis=0).to_html(), unsafe_allow_html=True)
    
# Sidebar ----
st.sidebar.markdown("**Unassigned Issues**")
for project in project_list:
    project_value, project_delta = d.build_assigned_project_tickets(project)
    st.sidebar.metric(project, project_value, delta=project_delta, delta_color="inverse", help=None, label_visibility="visible")
st.sidebar.markdown("---")
st.sidebar.markdown("**Total Assigned Issues**")
for person in team_list: 
    person_value, person_delta = d.build_tickets_assigned_for_a_person(project_list, person)
    st.sidebar.metric(person, person_value, delta=person_delta, delta_color="inverse", help=None, label_visibility="visible")

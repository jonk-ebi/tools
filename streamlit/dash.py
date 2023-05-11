import toml

import streamlit as st
import pandas as pd

from data import build_personal_load, build_issues, update_data, build_assigned_tickets, build_all_assigned_tickets

# TODO
# - factor in project people 
# - improve summary tables - highlights and index
# - add project links
# - add a new issues section to summary
# - add a my issues tab
# - days since assigned 
# - delta on summary

def load_settings(toml_path):
    with open(toml_path) as toml_stream:
        return toml.load(toml_stream)
        

def update_all_projects(projct_list, team_list, token): 
    for project in projct_list: 
        update_data(project, team_list, token)
        
config = load_settings("settings.toml")
project_list = config['settings']['projects']
team_list = config['settings']['team']
project_settings = {project:config[project] for project in project_list}
project_name_list = [f"{p} ({project_settings[p]['name']})" for p in project_list]

st.set_page_config(page_title="Ensembl Jira Dash", page_icon=":chart_with_upwards_trend:", layout="wide")

st.button("Refresh Data", on_click=update_all_projects, args=[project_list, team_list, config['jira']['token']], type="primary")

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
    df = build_personal_load(project)
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
        df = build_issues(project)
        st.write(f"{project_name} Issue board")
        st.markdown(df.style.bar(subset=['life'], color='#d65f5f').hide(axis=0).to_html(), unsafe_allow_html=True)
    
# Sidebar ----
st.sidebar.markdown("**Unassigned Issues**")
for project in project_list:
    project_value, project_delta = build_assigned_tickets(project)
    st.sidebar.metric(project, project_value, delta=None, delta_color="normal", help=None, label_visibility="visible")
st.sidebar.markdown("---")
st.sidebar.markdown("**Total Assigned Issues**")
for person in team_list: 
    person_value, person_delta = build_all_assigned_tickets(person, project_list)
    st.sidebar.metric(person, person_value, delta=None, delta_color="normal", help=None, label_visibility="visible")    
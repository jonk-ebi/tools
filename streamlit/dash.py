import streamlit as st
import pandas as pd

from data import build_personal_load, build_issues, update_data, build_unassigned_tickets

PROJECTS = ["ENSWEB","ENSWBSITES","ENSMVP"]
# TODO
# - Move projects to settings 
# - Expose people 
# - improve summary tables - highlights and index
# - add project links
# - add a new issues section to summary
# - add a my issues tab
# - days since assigned 


def update_all_projects(): 
    for project in PROJECTS: 
        update_data(project)

st.set_page_config(page_title="Ensembl Jira Dash", page_icon=":chart_with_upwards_trend:", layout="wide")

st.button("Refresh Data", on_click=update_all_projects, type="primary")

tab_names = ["Summary"]
tab_names.extend(PROJECTS)

tabs = st.tabs(tab_names)
summary_tab = tabs[0]
project_tabs = tabs[1:]

# Summary ----
with summary_tab:
    columns = st.columns(2)
    col_index = 0
    
for project in PROJECTS:
    df = build_personal_load(project)
    with columns[col_index]:
        st.write(f"{project} tickets")
        st.dataframe(df.style.background_gradient(cmap="Blues", vmin=0, vmax=100), use_container_width=True)
    col_index += 1
    if col_index >= len(columns):
        col_index = 0

# Project details ----
for x in range(0,len(project_tabs)):
    project = PROJECTS[x]
    with project_tabs[x]:
        df = build_issues(project)
        st.write(f"{project} Issue board")
        st.markdown(df.style.bar(subset=['life'], color='#d65f5f').hide(axis=0).to_html(), unsafe_allow_html=True)
    
# Sidebar ----
st.sidebar.write("Unassigned issues")
for project in PROJECTS:
    ensweb_value, ensweb_delta = build_unassigned_tickets(project)
    st.sidebar.metric(project, ensweb_value, delta=None, delta_color="normal", help=None, label_visibility="visible")
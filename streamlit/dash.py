import streamlit as st
import pandas as pd

from data import build_personal_load, build_issues, update_data, build_unassigned_tickets

PROJECTS = ["ENSWEB","ENSWBSITES","ENSMVP"]

def update_all_projects(): 
    for project in PROJECTS: 
        update_data(project)

#update_data()

#df["issue"] = df["issue"].apply

st.markdown(
    """
    <style>
        .block-container
        {
            max-width:unset;
            margin-left:1rem;
            margin-right:1rem;
        }
    </style>
    """, unsafe_allow_html=True
)

st.button("Refresh Data", on_click=update_all_projects, type="primary")

tab_names = ["Summary"]
tab_names.extend(PROJECTS)

print(tab_names)

tabs = st.tabs(tab_names)

summary_tab = tabs[0]

# Summary ----
with summary_tab:
    columns = st.columns(2)
    col_index = 0
    
for project in PROJECTS:
    df = build_personal_load(project)
    with columns[col_index]:
        st.write(f"{project} active tickets")
        st.dataframe(df, use_container_width=True)
    col_index += 1
    if col_index >= len(columns):
        col_index = 1

# Project details ----
for x in range(1,len(tabs)):
    project = PROJECTS[x -1]
    with tabs[x]:
        df = build_issues(project)
        st.write(f"{project} Issue board")
        st.markdown(df.style.bar(subset=['life'], color='#d65f5f').to_html(), unsafe_allow_html=True)
    

# Sidebar ----
st.sidebar.write("Unassigned issues")
for project in PROJECTS:
    ensweb_value, ensweb_delta = build_unassigned_tickets(project)
    st.sidebar.metric(project, ensweb_value, delta=None, delta_color="normal", help=None, label_visibility="visible")
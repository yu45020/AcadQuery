import streamlit as st

md_file = 'list_of_papers.md'
with open(md_file, 'r', encoding='utf-8') as f:
    content = f.read()
st.set_page_config(page_title="List of Papers", page_icon="",
                   layout='wide',
                   initial_sidebar_state='expanded'
                   )
st.sidebar.header("")
st.markdown(content, unsafe_allow_html=True)

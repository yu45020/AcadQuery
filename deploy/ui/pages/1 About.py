import streamlit as st

md_file = 'README.md'
with open(md_file, 'r', encoding='utf-8') as f:
    content = f.read()
st.set_page_config(page_title="Learn More About the Search", page_icon="",
                   layout='wide',
                   initial_sidebar_state='expanded'
                   )
st.sidebar.header("")
st.markdown(content, unsafe_allow_html=True)

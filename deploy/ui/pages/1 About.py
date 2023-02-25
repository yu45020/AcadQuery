import streamlit as st

md_file = 'README.md'


def set_state_if_absent(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


set_state_if_absent("content_page_1", None)

if st.session_state.content_page_1 is None:
    with open(md_file, 'r', encoding='utf-8') as f:
        st.session_state.content_page_1 = f.read()

st.set_page_config(page_title="Learn More About the Search", page_icon="",
                   layout='wide',
                   initial_sidebar_state='expanded'
                   )
st.sidebar.header("")
st.markdown(st.session_state.content_page_1, unsafe_allow_html=True)

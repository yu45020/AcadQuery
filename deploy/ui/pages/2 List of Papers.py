import streamlit as st

md_file = 'documents/list_of_papers.md'


def set_state_if_absent(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


set_state_if_absent("content_page_2", None)
if True:  # st.session_state.content_page_2 is None:
    with open(md_file, 'r', encoding='utf-8') as f:
        st.session_state.content_page_2 = f.read()

st.set_page_config(page_title="List of Papers", page_icon="",
                   layout='wide',
                   initial_sidebar_state='expanded'
                   )
st.sidebar.header("")
st.markdown(st.session_state.content_page_2, unsafe_allow_html=True)

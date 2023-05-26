#
import os
from json import JSONDecodeError
import logging

import streamlit as st
from annotated_text import annotation
from markdown import markdown

from ui.utils import query, haystack_version, haystack_init_
from ui.__init__ import version

# TODO: Rewrite API rest wait time
DEFAULT_QUESTION = "the weaknesses  of information processing"
DEFAULT_QUESTION_AT_STARTUP = os.getenv("DEFAULT_QUESTION_AT_STARTUP", DEFAULT_QUESTION)
DEFAULT_ANSWER_AT_STARTUP = os.getenv("DEFAULT_ANSWER_AT_STARTUP", " ")
ENABLE_SEARCH = True
# Sliders
DEFAULT_DOCS_FROM_RETRIEVER = int(os.getenv("DEFAULT_DOCS_FROM_RETRIEVER", "3"))
DEFAULT_NUMBER_OF_ANSWERS = int(os.getenv("DEFAULT_NUMBER_OF_ANSWERS", "3"))


def main():
    # Title
    st.set_page_config(page_title="Academic Paper Semantic Search",
                       page_icon="imgs/favicon.ico",
                       layout='wide',
                       initial_sidebar_state='auto',
                       menu_items={
                           'About': "# ☠👻👽👾🤖💩💀"
                       }
                       )

    st.markdown("# Academic Paper Semantic Search")
    st.markdown(f'<div style="text-align: right"> Version: {version} </div> ', unsafe_allow_html=True)

    def set_state_if_absent(key, value):
        if key not in st.session_state:
            st.session_state[key] = value

    default_query_pipe_dict = None

    set_state_if_absent("query_pipe", default_query_pipe_dict)
    set_state_if_absent("question", DEFAULT_QUESTION_AT_STARTUP)
    set_state_if_absent("last_question", '')

    set_state_if_absent("answer", DEFAULT_ANSWER_AT_STARTUP)
    set_state_if_absent("results_dense", None)
    set_state_if_absent("results_sparse", None)
    set_state_if_absent("result_type", None)

    set_state_if_absent("raw_json_dense", None)
    set_state_if_absent("raw_json_sparse", None)

    set_state_if_absent("random_question_requested", False)

    # Small callback to reset the interface in case the text of the question changes
    def reset_results(*args):
        st.session_state.answer = None
        st.session_state.results_dense = None
        st.session_state.results_sparse = None
        st.session_state.raw_json_sparse = None
        st.session_state.raw_json_dense = None
        st.session_state.result_type = None

    # Sidebar
    st.sidebar.header("Options")
    reader_top_k = st.sidebar.slider(
        "Max. number of answers",
        min_value=1,
        max_value=15,
        value=DEFAULT_NUMBER_OF_ANSWERS,
        step=1,
        on_change=reset_results,
    )
    retriever_top_k = st.sidebar.slider(
        "Max. number of documents from retriever",
        min_value=1,
        max_value=15,
        value=DEFAULT_DOCS_FROM_RETRIEVER,
        step=1,
        on_change=reset_results,
    )
    debug = st.sidebar.checkbox("Show debug info")

    st.sidebar.markdown(
        f"""
        <style>
            a {{
                text-decoration: none;
            }}
            .haystack-footer {{
                text-align: center;
            }}
            .haystack-footer h4 {{
                margin: 0.1rem;
                padding:0;
            }}
            footer {{
                opacity: 0;
            }}
        </style>
        <div class="haystack-footer">
            <hr />
            <h4>Built with <a href="https://haystack.deepset.ai/">Haystack</a></h4>
            <small>😫😪☕🥶👻☕💀</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search bar
    question = st.text_input(
        value=st.session_state.question,
        max_chars=100,
        on_change=None,
        label="question",
        label_visibility="hidden",
    )

    last_query = st.empty()
    # st.write('Last Query: ' + st.session_state.question)
    col1, = st.columns(1)
    col1.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)
    # col2.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)

    run_pressed = col1.button("Search")

    dense_result_tab, sparse_result_tab = st.columns(2)
    dense_result_tab.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)
    sparse_result_tab.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)

    dense_result_tab.subheader("Neural Search ")
    sparse_result_tab.subheader("Dictionary Search")

    def write_query_result(result_tab, search_result, search_raw):
        for count, result in enumerate(search_result):
            if result["answer"]:
                answer, context = result["answer"], result["document"]
                start_idx = context.find(answer)
                end_idx = start_idx + len(answer)
                relevance = result['answer_score']  # result['document_score']
                source = result['source']
                # Hack due to this bug: https://github.com/streamlit/streamlit/issues/3190
                result_tab.markdown(f"**Document:** {source} \n")
                result_tab.markdown(f"**Relevance:** {relevance}")
                result_tab.write(
                    markdown(context[:start_idx] + str(annotation(answer, "", "#edff87", "#080001")) + context[
                                                                                                               end_idx:]),
                    unsafe_allow_html=True,
                )
                result_tab.write("\n" + '-----' + '\n')
            else:
                st.session_state.info(
                    "🤔 &nbsp;&nbsp; Haystack is unsure whether any of the documents contain an answer to your question. Try to reformulate it!"
                )

        if debug:
            result_tab.subheader("REST API JSON response")
            result_tab.write(search_raw)
        # --------------------

    if run_pressed and question:
        st.session_state.question = question
        with dense_result_tab:
            with st.spinner(
                    f"🧠 &nbsp;&nbsp; Searching documents... \n "
            ):
                try:
                    st.session_state.results_dense, st.session_state.raw_json_dense = query(
                        question,
                        search_type='dense',
                        top_k_param_name='top_k',
                        reader_top_k=reader_top_k,
                        retriever_top_k=retriever_top_k
                    )
                    write_query_result(dense_result_tab, st.session_state.results_dense,
                                       st.session_state.raw_json_dense)
                except JSONDecodeError as je:
                    st.error("👓 &nbsp;&nbsp; An error occurred reading the results. Is the document store working?")
                    return
                except Exception as e:

                    if "The server is busy processing requests" in str(e) or "503" in str(e):
                        st.error("🧑‍🌾 &nbsp;&nbsp; All our workers are busy! Try again later.")
                    else:
                        st.error("🐞 &nbsp;&nbsp; An error occurred during the request.")
                        print(e)
                        return

        with sparse_result_tab:
            with st.spinner(
                    f"🧠 &nbsp;&nbsp; Searching documents ... \n "
            ):
                try:
                    st.session_state.results_sparse, st.session_state.raw_json_sparse = query(
                        question,
                        search_type='sparse',
                        top_k_param_name='top_k',
                        reader_top_k=reader_top_k,
                        retriever_top_k=retriever_top_k
                    )
                    write_query_result(sparse_result_tab, st.session_state.results_sparse,
                                       st.session_state.raw_json_sparse)

                except JSONDecodeError as je:
                    st.error("👓 &nbsp;&nbsp; An error occurred reading the results. Is the document store working?")
                    return
                except Exception as e:
                    logging.exception(e)
                    if "The server is busy processing requests" in str(e) or "503" in str(e):
                        st.error("🧑‍🌾 &nbsp;&nbsp; All our workers are busy! Try again later.")
                    else:
                        st.error("🐞 &nbsp;&nbsp; An error occurred during the request.")
                        return
        st.session_state.last_question = question
    else:
        if st.session_state.results_dense:
            write_query_result(dense_result_tab, st.session_state.results_dense,
                               st.session_state.raw_json_dense)

        if st.session_state.results_sparse:
            write_query_result(sparse_result_tab, st.session_state.results_sparse,
                               st.session_state.raw_json_sparse)
    last_query.write(f"Last Query: {st.session_state.last_question}")


# ------------------------
main()
#
# import requests
#
#
# query_result = requests.get(f"""
# http://127.0.0.1:7999/?question="brand"&retriever_top_k=3&reader_top_k=3&search_type="dense"
# """)
# a = query_result.json()
# [i  for i in a["answers"]][0].keys()

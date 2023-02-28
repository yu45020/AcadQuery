# pylint: disable=missing-timeout

import os
from typing import List, Dict, Any, Tuple, Optional

import requests
import streamlit as st

from ui.load_db import load_query_pipelines

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000")
STATUS = "initialized"
HS_VERSION = "hs_version"
DOC_REQUEST = "query"
DOC_FEEDBACK = "feedback"
DOC_UPLOAD = "file-upload"
 


def haystack_init_():
    query_pipe_dict = load_query_pipelines()
    return query_pipe_dict


@st.cache
def haystack_version():
    """
    Get the Haystack version from the REST API
    """
    url = f"{API_ENDPOINT}/{HS_VERSION}"
    return requests.get(url, timeout=0.1).json()["hs_version"]


def get_document_by_answer_id(documents: list, answer: dict):
    target_doc_id = answer['document_ids'][0]
    for doc in documents:
        if doc['id'] == target_doc_id:
            return doc
    raise ValueError


def query(query, query_pipe, top_k_param_name='top_k',
          filters={}, top_k_reader=5, top_k_retriever=5) -> Tuple[
    List[Dict[str, Any]], Dict[str, str]]:
    """
    Send a query to the REST API and parse the answer.
    Returns both a ready-to-use representation of the results and the raw JSON.
    """

    params = {"filters": filters,
              "Retriever": {top_k_param_name: top_k_retriever},
              "Reader": {"top_k": top_k_reader}}

    response = query_pipe.run(query=query, params=params)

    # Format response
    results = []
    answers = [i.to_dict() for i in response["answers"]]
    documents = [i.to_dict() for i in response['documents']]
    for answer in answers:
        if bool(answer):
            doc = get_document_by_answer_id(documents, answer)
            results.append(
                {
                    "context": "..." + answer["context"] + "...",
                    "answer": answer.get("answer", None),
                    'answer_score': round(answer['score'] * 100, 2),
                    "authors": answer["meta"]["authors"],
                    'title': answer['meta']['title'],
                    'year': answer['meta']['year'],
                    "document": doc['content'],
                    'document_score': round(doc['score'] * 100, 2),
                    'source': f"[{doc['meta']['authors']}] ({doc['meta']['year']}) {doc['meta']['title']}",
                    "offset_start_in_doc": answer["offsets_in_document"][0]["start"],
                    "_raw": answer,
                }
            )
        else:
            results.append(
                {
                    "context": None,
                    "answer": None,
                    "document": None,
                    "relevance": 0,
                    "_raw": None,
                }
            )
    return results, response


def send_feedback(query, answer_obj, is_correct_answer, is_correct_document, document) -> None:
    """
    Send a feedback (label) to the REST API
    """
    url = f"{API_ENDPOINT}/{DOC_FEEDBACK}"
    req = {
        "query": query,
        "document": document,
        "is_correct_answer": is_correct_answer,
        "is_correct_document": is_correct_document,
        "origin": "user-feedback",
        "answer": answer_obj,
    }
    response_raw = requests.post(url, json=req)
    if response_raw.status_code >= 400:
        raise ValueError(f"An error was returned [code {response_raw.status_code}]: {response_raw.json()}")


def upload_doc(file):
    url = f"{API_ENDPOINT}/{DOC_UPLOAD}"
    files = [("files", file)]
    response = requests.post(url, files=files).json()
    return response


def get_backlink(result) -> Tuple[Optional[str], Optional[str]]:
    if result.get("document", None):
        doc = result["document"]
        if isinstance(doc, dict):
            if doc.get("meta", None):
                if isinstance(doc["meta"], dict):
                    if doc["meta"].get("url", None) and doc["meta"].get("title", None):
                        return doc["meta"]["url"], doc["meta"]["title"]
    return None, None

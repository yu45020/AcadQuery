"""
Convert plain to database
Dense databases use FAISS, and sparse database use InMemory
"""
import glob
import os
import re

from haystack import Pipeline
from haystack.document_stores import FAISSDocumentStore, InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import TextConverter, PreProcessor

txt_files = "data/pdf/**/*.txt"


def get_meta_from_filename(file):
    name = os.path.basename(file)
    authors = re.search(r'\[.*\]', name)
    if bool(authors):
        authors = re.sub(r'\[|\]', '', authors.group())
    else:
        authors = ''

    year = re.search(r'\(.*\)', name)
    if bool(year):
        year = re.sub(r'\(|\)', '', year.group())
    else:
        year = ''
    title = re.sub(r'\[.*\)', '', name).replace('.txt', '').strip()
    return {'authors': authors, 'year': year, 'title': title}


files_to_index = glob.glob(txt_files, recursive=True)
file_meta = [get_meta_from_filename(i) for i in files_to_index]


def build_db(files_to_index, file_meta,
             db_folder, db_name, split_length=100, split_overlap=20,
             db_type='sparse',  # or 'dense'
             model_cpk=None,
             embedding_dim=768,
             similarity='dot_product',
             duplicate_documents='skip',
             use_openai=False,
             openai_key=None
             ):
    if not os.path.isdir(db_folder):
        os.mkdir(db_folder)
    db_path = f'{db_folder}/{db_name}.db'
    db_index = f"{db_folder}/{db_name}.faiss"
    db_config = f"{db_folder}/{db_name}.json"
    if db_type == 'dense':
        if not os.path.exists(db_path):
            document_store = FAISSDocumentStore(sql_url=f"sqlite:///{db_path}",
                                                faiss_index_factory_str="Flat",
                                                embedding_dim=embedding_dim,
                                                similarity=similarity,
                                                duplicate_documents=duplicate_documents)
        else:
            document_store = FAISSDocumentStore.load(index_path=db_index, config_path=db_config)
    else:
        document_store = InMemoryDocumentStore(use_bm25=True, bm25_algorithm='BM25Plus')

    doc_pipeline = Pipeline()
    text_converter = TextConverter()
    preprocessor = PreProcessor(
        clean_whitespace=True,
        clean_header_footer=True,
        clean_empty_lines=True,
        split_by="word",
        split_length=split_length,  # https://docs.haystack.deepset.ai/docs/optimization#document-length
        split_overlap=split_overlap,
        split_respect_sentence_boundary=True,
        language='en',
        max_chars_check=float('inf')
    )

    doc_pipeline.add_node(component=text_converter, name="TextConverter", inputs=["File"])
    doc_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["TextConverter"])
    doc_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

    doc_pipeline.run(file_paths=files_to_index, meta=file_meta)

    if db_type == 'dense' and not use_openai:
        retriever = EmbeddingRetriever(
            document_store=document_store,
            embedding_model=model_cpk,
            model_format="sentence_transformers",
        )
        document_store.update_embeddings(retriever)
        document_store.save(index_path=db_index, config_path=db_config)
    elif db_type == 'sparse':
        import joblib
        joblib.dump(document_store, db_path + '.pkl')
    elif db_type == 'dense' and use_openai:
        retriever = EmbeddingRetriever(
            document_store=document_store,
            embedding_model='text-embedding-ada-002',
            batch_size=8,
            max_seq_len=8192,
            api_key=openai_key
        )
        document_store.update_embeddings(retriever)
        document_store.save(index_path=db_index, config_path=db_config)

    else:
        raise ValueError


build_db(files_to_index=files_to_index,
         file_meta=file_meta,
         db_folder='data/db-faiss',
         db_name='dense-multi-qa-mpnet-base-dot-v1',
         split_length=100,
         split_overlap=5,
         db_type='dense',
         model_cpk="sentence-transformers/multi-qa-mpnet-base-dot-v1",
         embedding_dim=768,
         similarity='dot_product')

build_db(files_to_index=files_to_index,
         file_meta=file_meta,
         db_folder='data/db-faiss',
         db_name='dense-msmarco-distilbert-base-tas-b',
         split_length=100,  # the model is trained on 60 words on avg
         split_overlap=5,
         db_type='dense',
         model_cpk='sentence-transformers/msmarco-distilbert-base-tas-b',
         embedding_dim=768,
         similarity='dot_product')

build_db(files_to_index=files_to_index,
         file_meta=file_meta,
         db_folder='data/db-faiss',
         db_name='all-mpnet-base-v2',
         split_length=100,
         split_overlap=5,
         db_type='dense',
         model_cpk="sentence-transformers/all-mpnet-base-v2",
         embedding_dim=768,
         similarity='dot_product')

build_db(files_to_index=files_to_index,
         file_meta=file_meta,
         db_folder='data/db-inmemory',
         db_name='sparse-bm25plus-length-300',
         split_length=300,
         split_overlap=10,
         db_type='sparse')

# use openai
# with open('key', 'r', encoding='utf-8') as f:
#     open_key = f.read()

# build_db(files_to_index=files_to_index[:3],
#          file_meta=file_meta,
#          db_folder='data/db-openai',
#          db_name='openai',
#          split_length=100,
#          split_overlap=5,
#          db_type='dense',
#          model_cpk="",
#          embedding_dim=1536,
#          similarity='dot_product',
#          use_openai=True,
#          openai_key=open_key
#          )

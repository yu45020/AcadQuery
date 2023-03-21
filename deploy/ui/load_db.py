from haystack import Pipeline
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import BM25Retriever, EmbeddingRetriever, JoinDocuments, SentenceTransformersRanker
import joblib
from haystack.nodes import FARMReader


def load_faiss_db_store(db_folder, db_name):
    db_index = f"{db_folder}/{db_name}.faiss"
    db_config = f"{db_folder}/{db_name}.json"
    return FAISSDocumentStore.load(index_path=db_index, config_path=db_config)


def load_inmemory_db_store(db_folder, db_name):
    return joblib.load(f"{db_folder}/{db_name}.db.pkl")


def load_retriver(db_folder, db_name, db_type, model_cpk=None):
    if db_type == 'sparse':
        db_store = load_inmemory_db_store(db_folder, db_name)
        retriever = BM25Retriever(document_store=db_store, scale_score=False)
    elif db_type == 'dense':
        assert model_cpk is not None
        db_store = load_faiss_db_store(db_folder, db_name)
        retriever = EmbeddingRetriever(
            document_store=db_store,
            embedding_model=f"sentence-transformers/{model_cpk}",
            model_format="sentence_transformers",
            scale_score=True
        )
    else:
        raise ValueError
    return retriever


def load_query_pipelines():
    retriver_dense = load_retriver(db_folder='data/db-faiss',
                                   db_name='dense-multi-qa-mpnet-base-dot-v1',
                                   db_type='dense',
                                   model_cpk="multi-qa-mpnet-base-dot-v1"
                                   )
    # retriver = load_retriver(db_folder='data/db-faiss',
    #                                  db_name='dense-msmarco-distilbert-base-tas-b',
    #                                  db_type='dense',
    #                                  model_cpk="msmarco-distilbert-base-tas-b"
    #                                  )
    querying_dense_pipeline = Pipeline()
    reader_dense = FARMReader(model_name_or_path="deepset/roberta-base-squad2")
    # dense search
    querying_dense_pipeline.add_node(component=retriver_dense, name="Retriever", inputs=["Query"])
    querying_dense_pipeline.add_node(component=reader_dense, name="Reader", inputs=["Retriever"])
    # querying_dense_pipeline.run(query='brand')
    # sparse search
    retriver_bm25 = load_retriver(db_folder='data/db-inmemory',
                                  db_name='sparse-bm25plus-length-300',
                                  db_type='sparse'
                                  )
    reader_bm25 = FARMReader(model_name_or_path="deepset/roberta-base-squad2")

    ranker_bm25 = SentenceTransformersRanker(model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2")
    querying_sparse_pipeline = Pipeline()
    querying_sparse_pipeline.add_node(component=retriver_bm25, name="Retriever-bm25", inputs=["Query"])
    querying_sparse_pipeline.add_node(component=ranker_bm25, name="Retriever", inputs=["Retriever-bm25"])
    querying_sparse_pipeline.add_node(component=reader_bm25, name="Reader", inputs=["Retriever"])
    # querying_sparse_pipeline.run(query='brand', params={
    #     "Retriever": {'top_k': 3},
    #     "Reader": {"top_k": 3}
    # })
    return {'dense': querying_dense_pipeline,
            'sparse': querying_sparse_pipeline}

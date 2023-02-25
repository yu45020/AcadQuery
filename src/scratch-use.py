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


def load_retriver(db_folder, db_name, db_type, model_cpk):
    if db_type == 'sparse':
        db_store = load_inmemory_db_store(db_folder, db_name)
        retriever = BM25Retriever(document_store=db_store, scale_score=True)
    elif db_type == 'dense':
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


retriver_mpnet = load_retriver(db_folder='data/db-faiss',
                               db_name='dense-multi-qa-mpnet-base-dot-v1',
                               db_type='dense',
                               model_cpk="multi-qa-mpnet-base-dot-v1"
                               )
# retriver_msmarco = load_retriver(db_folder='data/db-faiss',
#                                  db_name='dense-msmarco-distilbert-base-tas-b',
#                                  db_type='dense',
#                                  model_cpk="msmarco-distilbert-base-tas-b"
#                                  )
#
# retriver_bm25 = load_retriver(db_folder='data/db-inmemory',
#                               db_name='sparse-bm25plus-length-300',
#                               db_type='sparse',
#                               model_cpk=None
#                               )
# ranker_bm25 = SentenceTransformersRanker(model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2")
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)

querying_pipeline = Pipeline()
querying_pipeline.add_node(component=retriver_mpnet, name="Retriever", inputs=["Query"])
querying_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

prediction = querying_pipeline.run(
    query="what's marketing mix?",  # "Who is the father of Arya Stark?",
    params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 10}
    }
)
answers = prediction['answers']
documents = prediction['documents']
answers[2]
documents[3]
##

retriver_mpnet = load_retriver(db_folder='data/db-faiss',
                               db_name='dense-multi-qa-mpnet-base-dot-v1',
                               db_type='dense',
                               model_cpk="multi-qa-mpnet-base-dot-v1"
                               )
retriver_msmarco = load_retriver(db_folder='data/db-faiss',
                                 db_name='dense-msmarco-distilbert-base-tas-b',
                                 db_type='dense',
                                 model_cpk="msmarco-distilbert-base-tas-b"
                                 )

querying_dense_pipeline = Pipeline()
document_joiner = JoinDocuments(join_mode="concatenate")
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)
# dense search
querying_dense_pipeline.add_node(component=retriver_mpnet, name="Retriever-mpnet", inputs=["Query"])
querying_dense_pipeline.add_node(component=retriver_msmarco, name="Retriever-msmarco", inputs=["Query"])

querying_dense_pipeline.add_node(component=document_joiner, name="Retriever",
                                 inputs=["Retriever-mpnet", "Retriever-msmarco"])
querying_dense_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])
prediction = querying_dense_pipeline.run(
    query="what's marketing mix?",  # "Who is the father of Arya Stark?",
    params={
        "Retriever": {"top_k_join": 3},
        "Reader": {"top_k": 5}
    }
)

b = [i.to_dict() for i in prediction['documents']]
len(a)
a = prediction['answers'][0]
a = a.to_dict()

b[0]
[doc for doc in b if doc["id"] == a["document_id"]][0]['content']

# sparse search
retriver_bm25 = load_retriver(db_folder='data/db-inmemory',
                              db_name='sparse-bm25plus-length-300',
                              db_type='sparse',
                              model_cpk=None
                              )
ranker_bm25 = SentenceTransformersRanker(model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2")
querying_sparse_pipeline = Pipeline()
querying_sparse_pipeline.add_node(component=retriver_bm25, name="Retriever-bm25", inputs=["Query"])
querying_sparse_pipeline.add_node(component=ranker_bm25, name="Retriever", inputs=["Retriever-bm25"])
querying_sparse_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

from fastapi import FastAPI

from ui.load_db import load_query_pipelines

app = FastAPI()
query_pipe_dict = load_query_pipelines()


@app.get("/")
async def query_api(question,
                    retriever_top_k,
                    reader_top_k,
                    search_type):
    print(search_type)
    response = query_pipe_dict[search_type].run(query=question, params={
        "Retriever": {'top_k': int(retriever_top_k)},
        "Reader": {"top_k": int(reader_top_k)}
    })

    return response

# python -m uvicorn   search_rest_gunicorn:app --host 127.0.0.1 --port 7999 --reload
# http://127.0.0.1:7999/?question="brand"&retriever_top_k=3&reader_top_k=3&search_type=dense
# @app.get("/")
# async def query_api(question, question,):
#     data = request.data()
#     question = data['question']
#     search_type = data['search_type']
#     retriever_top_k = data['retriever_top_k']
#     reader_top_k = data['reader_top_k']
#
#     response = query_pipe_dict[search_type].run(query=question, params={
#         "Retriever": {'top_k': retriever_top_k},
#         "Reader": {"top_k": reader_top_k}
#     })
#     print(response)
#     return response

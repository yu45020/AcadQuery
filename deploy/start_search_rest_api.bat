
%~dp0./env/python.exe -m uvicorn rest_api.search_rest_gunicorn:app --host 127.0.0.1 --port 7999 --workers 1 
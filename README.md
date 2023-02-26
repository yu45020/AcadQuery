# Academic Paper Semantic Search

--------


Academic Paper Semantic Search is a local search engine. It provides plain text search on a collection of pdf papers.
Search methods include neural network based search (BERT based) and simple dictionary based matching (`BM25`).

Version `α:1.4`

## How To Start Web Server
1. Create virtual environment. Recommend ``mamba`` rather than `conda` to install packages
  ```cmd
  conda create -p env/  python=3.9 
  conda activate env/
  pip install --upgrade pip
  pip install farm-haystack[sql,only-faiss,inmemorygraph]  streamlit st-annotated-text
  ```

2. You may want the GPU version if possible
  ```cmd 
  conda activate env/
  conda install -c conda-forge libfaiss-avx2
  pip install transformers[torch]
  ```

2. Copy `data/db-*` to `deploy/` and run
  ```cmd  
  cd deploy
  python -m streamlit run ui/Search.py --server.runOnSave=true --server.address=127.0.0.1
  ``` 

**Note**: without the ``--server.address=127.0.0.1``, `streamlit`will broadcast your ip address to the world.

## How to Build From Scratch

### Prepare PDF

* Install Zotera, and plug-in ``ZotFile`` and ``DOI Manager``
    * `Tool -> ZotFile Preference-> use subfolder defined by`: `[%a](%y){ %t}`
    * `ZotFile Preference-> Renaming Rules -> Format for all item & Patents`: `[%a](%y){ %t}`
    * `ZotFile Preference-> Tablet Settings`: check `use ZotFile to send and get files from tablet`, and
      set `base folder`
* Import pdf papers into Zotero, obtain `doi` and clean up metadata
* Select all pdf and right click, management attachments, sent to tablet
* Use `Adobe Pro` or `Abbyy` for batch text recognition

### Extract Plain Text

Use virtual environment to manage python packages. Many of them may have conflict with your current packages.

* Download [GROBID](https://github.com/kermitt2/grobid) docker image and the
  python [client](https://github.com/kermitt2/grobid_client_python).
  The [CRT-only](https://grobid.readthedocs.io/en/latest/Grobid-docker/#crf-only-image) is enough.
* Run `src/extract_text.py` to convert pdf to `tei.xml` format and parse them into plain text
* May need spell check

### Build Database
* Recommend  ``mamba`` to install packages
* Install [haystack](https://github.com/deepset-ai/haystack) python package or docker image
    * need to install faiss; given the small number of documents, the cpu version is fast enough
    * if possible, recommend `` mamba install -c conda-forge libfaiss-avx2 ``
    * if want to embed documents, need `transformer[torch]` package
*  `git clone https://github.com/kermitt2/grobid_client_python`
* run `src/build_database.py`
* Simple dictionary search use [BM25](https://docs.haystack.deepset.ai/docs/retriever#bm25-recommended) and In Memory
  database.
    * Documents are chunked into sentences. Each has at most 300 words with 10 words overlap.
    * May need to tune sentence length for better performance
* Neural Network based search use [sentence-transformer](https://www.sbert.net/) to embed words. Data are stored
  in [FAISS](https://github.com/facebookresearch/faiss)
    * Documents are chunked into sentences with at most 100 words
    * Embedding model use (need GPU for fast process)
        * `sentence-transformers/multi-qa-mpnet-base-dot-v1`
        * `sentence-transformers/msmarco-distilbert-base-tas-b`
* databases are in the ``data`` folder. Copy `db-faiss` and `db-inmemory` to `deploy/data/`

### Build Web Server

* Copy the [haystack-demos](https://github.com/deepset-ai/haystack-demos) and modify scripts in the ``ui`` folder. The
  main part is `webapp.py`
* The sample scripts use ``haystack`` api and docker, but you can run your script directly without docker.

### Build FAISS From Source

Windows users who have Intel cpu and want faster matching speed may want to compile it from source. You can manually
link the MKL library for faster speed.

* Install  `visual studio 2019`  (desktop development with C++), `cuda toolkit`, `Intel OneAPI toolkit`,
  and `swig`
* use conda env to activate desired python version
* assume install with default settings, in ``cmd``, activate environment variables

  ```cmd
  "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
  "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.7\bin\nvvp.bat"
  ```
  MKL library will be loaded automatically. If you don't need GPU, set `-DFAISS_ENABLE_GPU=OFF`

  ```cmd
  "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" -B build ^ 
    -DFAISS_ENABLE_PYTHON=ON ^
    -DFAISS_ENABLE_GPU=ON ^
    -DBUILD_SHARED_LIBS=ON ^ 
    -DCUDAToolkit_ROOT="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/" ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DFAISS_OPT_LEVEL=general ^
    -DBUILD_TESTING=OFF ^
    -DPython_EXECUTABLE="path to your python.exe" ^
    -DBLA_VENDOR=Intel10_64_dyn    
  ```
* Open `faiss/build/ALL_BUILD.vcxproj` with Visual Studio 2019; select `release` and then build `swigfaiss`
* Build wheel
  ```cmd
  cd build/faiss/python/
  python setup.py bdist_wheel
  ```

## TODO

* Spell check for plain text
* Fine tune embedding models
* Check quality & runtime for joint model: combine multiple embedding models for neural network based search 
from utils import init_chromadb, init_dataset

def init_chromadb_wrapper():
    embeddings, metadatas, documents, ids = init_dataset()
    client, collection = init_chromadb(embeddings, metadatas, documents, ids)
    return client, collection


    
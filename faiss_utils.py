import faiss
import os
import pickle
from config import FAISS_INDEX_PATH, METADATA_PATH

def load_faiss_index():
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata
    return None, None

def save_faiss_index(index, metadata):
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

def reset_index():
    if os.path.exists(FAISS_INDEX_PATH): os.remove(FAISS_INDEX_PATH)
    if os.path.exists(METADATA_PATH): os.remove(METADATA_PATH)

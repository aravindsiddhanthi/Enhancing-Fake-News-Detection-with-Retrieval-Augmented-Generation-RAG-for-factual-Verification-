import os
import pandas as pd
import faiss
from config import *
from helpers.faiss_utils import load_faiss_index, save_faiss_index, reset_index
from helpers.embedding import generate_embeddings
from helpers.formatter import format_date


print("TRAINING STARTED")
training_files = ['scraped_results/politifact_articles.csv','scraped_results/factcheck_articles.csv']

def train_files(training_files):
    for each_file in training_files:
        print(f"Training Started for file - {each_file}")
        try:
            df = pd.read_csv(each_file)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(each_file, encoding='latin1')
            except Exception as e:
                print(f"Training Failed while reading with latin1. Error - {e}")
                df = None
        except Exception as e:
            print(f"Training Failed. Error - {e}")
            return
        combined_text = df[TITLE_COL].fillna('') + " " + df[DESC_COL].fillna('')
        embeddings = generate_embeddings(combined_text.tolist())
        faiss_index, news_metadata = load_faiss_index()
        if faiss_index is not None and news_metadata:
            faiss_index.add(embeddings)
            news_metadata.extend(df.to_dict(orient="records"))
        else:
            faiss_index = faiss.IndexFlatIP(embeddings.shape[1])
            faiss_index.add(embeddings)
            news_metadata = df.to_dict(orient="records")

        save_faiss_index(faiss_index, news_metadata)
        print(f"Training Completed for file - {each_file}")
train_files(training_files)

import os
from dotenv import load_dotenv

load_dotenv()

FAISS_INDEX_PATH = "data/news_faiss.index"
METADATA_PATH = "data/news_metadata.pkl"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

TITLE_COL = 'Title'
DESC_COL = 'Description'
DATE_COL = 'Date'
URL_COL = 'URL'

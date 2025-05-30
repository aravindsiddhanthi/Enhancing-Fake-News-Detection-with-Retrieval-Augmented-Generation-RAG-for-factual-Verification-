import streamlit as st
from config import *
from helpers.file_loader import load_data
from helpers.faiss_utils import load_faiss_index, save_faiss_index, reset_index
from helpers.embedding import generate_embeddings
from helpers.response_generator import get_relevant_news, generate_response
from helpers.formatter import format_date
import os

st.set_page_config(page_title="News RAG Chatbot", page_icon="📰", layout="centered")

faiss_index, news_metadata = load_faiss_index()




st.title(" US Political News Chatbot ")

if faiss_index is None:
    st.info("Please upload and train a news file to begin.")
else:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question about the news...")

    if user_input:
        with st.chat_message("user"):
            answer, urls, dates= "","",""
            st.markdown(user_input)

        temp_history = st.session_state.chat_history + [{"role": "user", "content": user_input}]
        urls=[]

        with st.spinner("Searching news and generating response..."):

            relevant = get_relevant_news(user_input, faiss_index, news_metadata)
            answer, urls, dates = generate_response(user_input, relevant, temp_history)

        with st.chat_message("assistant"):
            st.markdown(answer)
            if dates:
                st.markdown("**Dates:** " + ", ".join([format_date(d) for d in dates]))
            if urls:
                st.markdown("**Sources:**")
                for url in urls:
                    st.markdown(f"- [{url}]({url})")

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

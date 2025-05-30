import google.generativeai as genai
from config import GOOGLE_API_KEY, TITLE_COL, DESC_COL, DATE_COL, URL_COL
from helpers.formatter import format_date
from sentence_transformers import SentenceTransformer
import faiss

genai.configure(api_key=GOOGLE_API_KEY)

def get_relevant_news(query, index, metadata, top_k=3):
    if index is None or metadata is None:
        return []

    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])[0].astype("float32")
    faiss.normalize_L2(query_embedding.reshape(1, -1))

    distances, indices = index.search(query_embedding.reshape(1, -1), top_k)

    relevant = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            item = metadata[idx]
            sim = distances[0][i]
            if sim > 0.2:
                relevant.append({
                    'title': item.get(TITLE_COL, ''),
                    'description': item.get(DESC_COL, ''),
                    'date': item.get(DATE_COL) if DATE_COL else None,
                    'url': item.get(URL_COL) if URL_COL else None,
                    'similarity': sim
                })

    return relevant


def generate_response(query, relevant_news, chat_history):
    if not relevant_news:
        return "No relevant news found.", [], []

    context = ""
    urls = []
    dates = []

    for news in relevant_news:
        context += f"Title: {news['title']}\nDescription: {news['description']}\n"
        if news['date']:
            context += f"Date: {format_date(news['date'])}\n"
            dates.append(news['date'])
        context += "\n"
        if news['url']: urls.append(news['url'])

    formatted_history = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {msg['content']}\n"

    formatted_history += f"User: {query}\n"

    prompt = f"""
        You are a helpful assistant that responds based only on the provided news articles.

        Your tasks depend on the type of user input:

        1. **If the user asks a question**:
           - Answer the question in a friendly and informative way.
           - Only use the context from the news articles.
           - If the answer isn't in the news, politely say you don’t have enough information.

        2. **If the user makes a statement** (e.g., a claim or fact):
           - Check if the statement is supported by the news context.
           - Respond with one of the following:
             - **Legit News: True (100%)** — if the statement is clearly and directly supported.
             - **Legit News: False (0%)** — if the statement is clearly contradicted by the news.
             - **Legit News: Can't verify** — if there isn’t enough information to confirm or deny it.
           - Optionally, add a short sentence explaining why, based on the news context.

        General guidelines:
            - Do not use bold text, italic formatting, markdown symbols, or code blocks.
            - Keep the font and tone consistent and neutral throughout the entire response.
            - Do not hallucinate or invent any information not present in the articles.

        You are also allowed to:
        - Greet the user politely if they say hello
        - Engage in friendly small talk (e.g., respond to "how are you?")

        Never make up facts or hallucinate news content. Stick strictly to the context provided.

        Here is the recent conversation:
        {formatted_history}

        Here are the relevant news articles:
        {context}

        Respond to the most recent user message using the above rules.
        """


    gen_config = {
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 32,
    }

    model = genai.GenerativeModel("gemini-1.5-flash", generation_config=gen_config)
    response = model.generate_content(prompt)
    return response.text, urls, dates

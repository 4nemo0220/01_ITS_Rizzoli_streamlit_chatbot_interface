import streamlit as st
from dotenv import load_dotenv
import os
import requests
import shelve
import json

load_dotenv()

st.title("ITS Chatbot Demo")

USER_AVATAR = "👤"
BOT_AVATAR = "🧠"

# Imposta modello di default (Ollama)
if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = "llama3"

# Carica chat salvate
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Salva chat
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Inizializza chat
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar per cancellare la cronologia
with st.sidebar:
    st.image("ITS_logo.png")
    st.divider()
    if st.button("🗑️ Cancella cronologia chat"):
        st.session_state.messages = []
        save_chat_history([])
    st.caption("Tutti i diritti riservati")

# Mostra messaggi precedenti
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---- STREAMING con Ollama ----
def stream_ollama(prompt, model="llama3", timeout=300):
    """
    Generatore che restituisce chunk di testo dallo stream di Ollama.
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}
    try:
        with requests.post(url, json=payload, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "response" in obj and obj["response"]:
                    yield obj["response"]
                if obj.get("done"):
                    break
    except requests.RequestException as e:
        yield f"\n\n❌ Errore di streaming da Ollama: {e}"

# Interfaccia chat principale
if prompt := st.chat_input("Scrivi un messaggio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("⌛ Sto pensando..."):
            placeholder = st.empty()
            buffer = ""
            # stream live
            for chunk in stream_ollama(prompt, st.session_state["ollama_model"]):
                buffer += chunk
                placeholder.markdown(buffer + "▌")  # cursore
            placeholder.markdown(buffer)


    st.session_state.messages.append({"role": "assistant", "content": buffer})
    save_chat_history(st.session_state.messages)
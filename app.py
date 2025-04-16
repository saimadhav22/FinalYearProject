import streamlit as st
from llm_handler import load_normal_chain, load_pdf_chat_chain
from langchain.memory import StreamlitChatMessageHistory
from streamlit_mic_recorder import mic_recorder
from utils import save_chat_history_json, get_timestamp, load_chat_history_json
from audio_handler import transcribe_audio
from pdf_handler import add_documents_to_db
from html_templates import get_bot_template, get_user_template, css
import yaml
import os
from llm_handler import debug_retrieve


with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def load_chain(chat_history):
    if st.session_state.pdf_chat:
        print("loading pdf chat chain")
        return load_pdf_chat_chain(chat_history)
    return load_normal_chain(chat_history)

def clear_input_field():
    if st.session_state.user_question == "":
        st.session_state.user_question = st.session_state.user_input
        st.session_state.user_input = ""

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def toggle_pdf_chat():
    st.session_state.pdf_chat = True

def save_chat_history():
    if st.session_state.history != []:
        if st.session_state.session_key == "new_session":
            st.session_state.new_session_key = get_timestamp() + ".json"
            save_chat_history_json(st.session_state.history, config["chat_history_path"] + st.session_state.new_session_key)
        else:
            save_chat_history_json(st.session_state.history, config["chat_history_path"] + st.session_state.session_key)

def main():
    st.title("Chat with AI")
    st.write(css, unsafe_allow_html=True)
    
    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])

    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
    if st.session_state.session_key == "new_session" and st.session_state.new_session_key != None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index)
    st.sidebar.toggle("PDF Chat", key="pdf_chat", value=False)

    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(config["chat_history_path"] + st.session_state.session_key)
    else:
        st.session_state.history = []

    chat_history = StreamlitChatMessageHistory(key="history")
    
    user_input = st.text_input("Type your message here", key="user_input", on_change=set_send_input)

    voice_recording_column, send_button_column = st.columns(2)
    chat_container = st.container()
    with voice_recording_column:
        voice_recording=mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording", just_once=True)
    with send_button_column:
        send_button = st.button("Send", key="send_button", on_click=clear_input_field)

    uploaded_audio = st.sidebar.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
    uploaded_pdf = st.sidebar.file_uploader("Upload a pdf file", accept_multiple_files=True, key="pdf_upload", type=["pdf"], on_change=toggle_pdf_chat)

    if uploaded_pdf:
        with st.spinner("Processing PDF..."):
            add_documents_to_db(uploaded_pdf)
    
    if uploaded_audio:
        transcribed_audio = transcribe_audio(uploaded_audio.getvalue())
        print(transcribed_audio)
        llm_chain = load_chain(chat_history)
        llm_chain.run("Summarize this text: " + transcribed_audio)

    if voice_recording:
        transcribed_audio = transcribe_audio(voice_recording["bytes"])
        print(transcribed_audio)
        llm_chain = load_chain(chat_history)
        llm_chain.run(transcribed_audio)

    if send_button or st.session_state.send_input:
        if st.session_state.user_question != "":
            llm_chain = load_chain(chat_history)
            llm_response = llm_chain.run(st.session_state.user_question)

            # Debugging: Print response in the terminal
            print("AI Response:", llm_response)

            # Ensure response is not empty
            if not llm_response or llm_response.strip() == "":
                llm_response = "[WARNING] No relevant information found. Try asking differently!"

            st.session_state.user_question = ""
            st.write(llm_response)

        st.session_state.send_input = False

    if chat_history.messages != []:
        with chat_container:
            st.write("Chat History:")
            for message in reversed(chat_history.messages):
                if message.type == "human":
                    st.write(get_user_template(message.content), unsafe_allow_html=True)
                else:
                    st.write(get_bot_template(message.content), unsafe_allow_html=True)

    save_chat_history()

if __name__ == "__main__":
    main()

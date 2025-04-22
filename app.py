import streamlit as st
import requests
import json

# Slider
temp = st.sidebar.slider(
    'Temperature',
    0, 100,
    label_visibility="visible",
    help="Adjust higher temperature for more creativity"
)

top_p = st.sidebar.slider(
    'Top P',
    0, 100, 20,
    label_visibility="visible",
    help="Adjust higher temperature for more creativity"
)

top_k = st.sidebar.slider(
    'Top K',
    0, 100,
    label_visibility="visible",
    help="Adjust higher temperature for more creativity"
)

st.title("Echo Bot")


@st.cache_resource
def get_messages():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    return st.session_state.messages


st.session_state.messages = get_messages()

# Initialize session state
if "generating_response" not in st.session_state:
    st.session_state.generating_response = False
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False
if "full_response" not in st.session_state:
    st.session_state.full_response = ""

def stop_generation():
    st.session_state.stop_generation = True
    st.session_state.generating_response = False
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.full_response})
    st.chat_message("assistant").markdown(st.session_state.full_response)
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def call_llm(prompt: str):
    # The API endpoint
    url = "http://127.0.0.1:8000/stream-chat"

    # Data to be sent
    data = {
        "prompt": str(prompt)
    }

    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()  # Raise HTTP errors

        for line in response.iter_lines():
            line_str = line.decode('utf-8').strip()
            if line_str.startswith('data: '):
                line_str = line_str[6:]

            try:
                chunk = json.loads(line_str)
                if "response" in chunk:
                    yield chunk["response"]
                    print("Chunk:", chunk)  # Debug streaming
            except json.JSONDecodeError:
                    continue
    
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")


if prompt := st.chat_input(
        "Ask questions and attach csv files",
        accept_file=True,
        file_type=["csv"],
    ):

    st.session_state.generating_response = True


    # Extract text and files
    text_prompt = prompt.text
    file_prompt = prompt.files

    st.chat_message("user").markdown(text_prompt)
    st.session_state.messages.append({"role": "user", "content": text_prompt})
    if st.session_state.generating_response and st.button("⏹️ Stop Generation", key="stop", on_click=stop_generation):
        pass

    print(f"----> Prompt: {text_prompt}")
    print(f"----> Generating response: {st.session_state.generating_response}")

    # Prepare assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()  # Create a placeholder
        st.session_state.full_response = ""
        
        # Stream the response word-by-word
        for word_chunk in call_llm(text_prompt):
            st.session_state.full_response += word_chunk
            response_placeholder.markdown(st.session_state.full_response + "▌")  # Typing effect
        
        # Final render (without cursor)
        response_placeholder.markdown(st.session_state.full_response)

        # Save to session state
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.full_response})
    
    st.session_state.generating_response = False
        
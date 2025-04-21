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

def ask_llm(prompt):
    print("hello---")
    # The API endpoint
    url = "http://localhost:11434/api/generate"

    # Data to be sent
    data = {
        "model": "deepseek-r1:7b",
        "prompt": str(prompt),
        "stream": True
    }

    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()  # Raise HTTP errors

        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                if "response" in chunk:
                    full_response += chunk["response"]
                print("Chunk:", chunk)  # Debug streaming

        return {"response": full_response}

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return {"error": "Invalid API response"}


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(
        "Ask questions and attach csv files",
        accept_file=True,
        file_type=["csv"],
    ):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = ask_llm(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
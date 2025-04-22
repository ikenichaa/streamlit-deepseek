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


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generating_response" not in st.session_state:
    st.session_state.generating_response = False
if "full_response" not in st.session_state:
    st.session_state.full_response = ""

@st.cache_resource
def get_messages():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    return st.session_state.messages

def stop_generation():
    st.session_state.stop_generation = True
    st.session_state.generating_response = False
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.full_response})


st.session_state.messages = get_messages()

# Display all existing messages first
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process new user input
if prompt := st.chat_input("Ask questions...", accept_file=True, file_type=["csv"]):
    # Reset for new generation
    st.session_state.full_response = ""

    text_input = prompt.text
    file_input = prompt.files
    
    # Store user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": text_input})
    st.session_state.generating_response = True
    if st.button("⏹️ Stop Generation", key="stop", on_click=stop_generation):
        pass

    # Generate assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        for chunk in call_llm(text_input):  # Your generator function
            if not st.session_state.generating_response:
                break
                
            st.session_state.full_response += chunk
            response_placeholder.markdown(st.session_state.full_response + "▌")
        
        # Finalize response
        response_placeholder.markdown(st.session_state.full_response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": st.session_state.full_response
        })

        st.session_state.generating_response = False  # Generation complete
    
    # Rerun to remove the stop button
    # when the response is done
    st.rerun()
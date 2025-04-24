import streamlit as st
import requests
import json

# Slider
temperature = st.sidebar.slider(
    'Temperature',
    0.0, 2.0, 0.6,
    label_visibility="visible",
    help="Temperature sampling flattens or sharpens the probability distribution over the tokens to be sampled"
)

top_p = st.sidebar.slider(
    'Top P',
    0.0, 1.0, 0.95,
    label_visibility="visible",
    help="Top-p sampling samples tokens with the highest probability scores until the sum of the scores reaches the specified threshold value"
)

top_k = st.sidebar.slider(
    'Top K',
    0, 100, 40,
    label_visibility="visible",
    help="Top-k sampling samples tokens with the highest probabilities until the specified number of tokens is reached."
)

st.title("Deep Seek")

def call_llm(prompt: str, option):
    print("Option---->", option)
    # The API endpoint
    url = "http://127.0.0.1:8000/stream-chat"

    # Data to be sent
    data = {
        "prompt": str(prompt),
        "option": {
            "temperature": option["temperature"],
            "top_p": option["top_p"],
            "top_k": option["top_k"]
        }
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
    st.chat_message("user").markdown(text_input)
    st.session_state.messages.append({"role": "user", "content": text_input})
    st.session_state.generating_response = True
    if st.button("⏹️ Stop Generation", key="stop", on_click=stop_generation):
        pass

    # Generate assistant response
    with st.chat_message("assistant"):
        tab_think, tab_answer = st.tabs(["Thinking", "Answer"])
        think_placeholder = st.empty()
        answer_placeholder = st.empty()

        think_response = ""
        answer_response = ""

        # Phase 1: Show spinner until first chunk arrives
        with st.spinner("Generating response..."):
            llm_stream = call_llm(
                            text_input, 
                            option={
                                "temperature": temperature,
                                "top_p": top_p,
                                "top_k": top_k
                            }
                        )
            first_chunk = next(llm_stream)  # Force first chunk
            if first_chunk != "<think>":
                st.session_state.full_response += first_chunk
                # think_placeholder.markdown(first_chunk + "▌")
        
        # Phase 2: Stream remaining chunks
        finish_thinking = False
        for chunk in llm_stream:
            if not st.session_state.generating_response:
                break

            if chunk == "</think>":
                finish_thinking = True
                continue

            if finish_thinking:
                answer_response += chunk
            else:
                think_response += chunk

            with tab_think:
               think_placeholder.markdown(think_response) 
            
            with tab_answer:
               answer_placeholder.markdown(answer_response) 
            # st.session_state.full_response += chunk
            # think_placeholder.markdown(st.session_state.full_response + "▌")
            
        # Finalize response
        think_placeholder.markdown(st.session_state.full_response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_response
        })

        st.session_state.generating_response = False  # Generation complete
    
    # Rerun to remove the stop button
    # when the response is done
    st.rerun()
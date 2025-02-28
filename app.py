import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

conn = psycopg2.connect(DATABASE_URL)  # PAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# database connection
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Please check your .env file.")

# Establish database connection
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("SELECT NOW();")  
print(cursor.fetchone())
cursor.close()
conn.close()



# Load environment variables
load_dotenv()

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error(" GOOGLE_API_KEY is missing! Please check your .env file.")
    st.stop()

@st.cache_resource
def load_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7,
        # max_output_tokens=800
        max_output_tokens=2048 
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly AI assistant. Provide clear and insightful responses."),
        ("user", "Question: {question}")
    ])
    return prompt | llm | StrOutputParser()

chain = load_chain()

def apply_theme():
    theme = """
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: %s;
            color: %s;
            padding-bottom: 100px !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: %s !important;
            color: %s !important;
        }
        
        .stChatFloatingInputContainer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 1rem;
            background: %s !important;
            z-index: 100;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }
        
        .stTextInput input {
            color: %s !important;
            background-color: %s !important;
            border: 1px solid %s !important;
        }
        
        .stButton button {
            background-color: %s !important;
            color: %s !important;
            border: 1px solid %s !important;
        }
        
        .message {
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 15px;
            max-width: 80%%;
            animation: fadeIn 0.3s ease-in;
        }
        
        .user-message {
            background: %s;
            color: %s;
            margin-left: auto;
        }
        
        .assistant-message {
            background: %s;
            color: %s;
            margin-right: auto;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @media (max-width: 600px) {
            .message {
                max-width: 90%%;
                padding: 10px 12px;
                font-size: 14px;
            }
            .stChatFloatingInputContainer {
                padding: 0.5rem;
            }
        }
    </style>
    """
    
    if st.session_state.dark_mode:
        st.markdown(theme % (
            "#1a1a1a", "#ffffff",       # Main container
            "#2d2d2d", "#ffffff",       # Sidebar
            "#2d2d2d",                  # Input container
            "#ffffff", "#404040", "#555555",  # Input field
            "#4CAF50", "#ffffff", "#4CAF50",  # Button
            "#004456", "#ffffff",        # User message
            "#2d3b2d", "#ffffff"        # Assistant message
        ), unsafe_allow_html=True)
    else:
        st.markdown(theme % (
            "#ffffff", "#333333",       # Main container
            "#f0f2f6", "#333333",       # Sidebar
            "#ffffff",                  # Input container
            "#333333", "#ffffff", "#cccccc",  # Input field
            "#4CAF50", "#ffffff", "#4CAF50",  # Button
            "#005f73", "#ffffff",      # User message
            "#e8f5e9", "#333333"       # Assistant message
        ), unsafe_allow_html=True)

# Header with LinkedIn
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.title("💬 AI Chat Assistant 🤖 ")
    st.title("🔍 Langchin + Gemini AI ")
    st.caption("🚀 Powered by Google Gemini 🌐 | Created by [Suraj Badre 🙏 ](https://github.com/badre-suraj-)")

    # st.caption(" Powered by Google Gemini [Created by suraj badre]")
    
with header_col2:
    st.markdown("""
    <div style="text-align: right; margin-top: 15px;">
        <a href="https://www.linkedin.com/in/suraj-badre/" target="_blank">
           <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
        </a>
    </div>
    """, unsafe_allow_html=True)

apply_theme()

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="message {message["role"]}-message">{message["content"]}</div>', 
                    unsafe_allow_html=True)


# Fixed bottom input
with st.container():
    col1, col2 = st.columns([6, 1])
    with col1:
        prompt = st.text_input(
            "Type your message here...",
            label_visibility="collapsed",
            key="input_field",
            placeholder="Ask me anything"  # <-- Add this line
        )
    with col2:
        generate = st.button("Generate", key="generate_btn")

if generate and prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="message user-message">{prompt}</div>', unsafe_allow_html=True)
    with st.chat_message("assistant"):
        with st.spinner("🤖 Thinking..."):
            response = chain.invoke({"question": prompt})
            st.markdown(f'<div class="message assistant-message">{response}</div>', 
                        unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})


# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🌙 Night Mode" if not st.session_state.dark_mode else "☀️ Day Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.subheader("💡 Example Questions")
    examples = [
        "Explain quantum computing in simple terms",
        "How do I make a HTTP request in Python?",
        "What's the difference between AI and ML?",
        "Suggest healthy breakfast ideas"
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": example})
            st.rerun()




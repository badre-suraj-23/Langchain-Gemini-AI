import streamlit as st
import os
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ----------------- API CONFIG -----------------
API_BASE = "https://blogmedia.onrender.com/api"

def login(email, password):
    url = f"{API_BASE}/login/"
    r = requests.post(url, data={"email": email, "password": password})
    if r.status_code == 200:
        return r.json().get("access")
    return None

def register(username, email, password):
    url = f"{API_BASE}/register/"
    r = requests.post(url, data={
        "username": username,
        "email": email,
        "password": password
    })
    return r

# ----------------- SESSION INIT -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "token" not in st.session_state:
    st.session_state.token = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ----------------- LLM INIT -----------------
load_dotenv()
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
        max_output_tokens=2048
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly AI assistant. Provide clear and insightful responses."),
        ("user", "Question: {question}")
    ])
    return prompt | llm | StrOutputParser()

chain = load_chain()

# ----------------- THEME -----------------
def apply_theme():
    theme = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: %s; color: %s; padding-bottom: 100px !important;}
        [data-testid="stSidebar"] {background-color: %s !important; color: %s !important;}
        .stChatFloatingInputContainer {position: fixed; bottom: 0; left: 0; right: 0; padding: 1rem; background: %s !important; z-index: 100; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);}
        .stTextInput input {color: %s !important; background-color: %s !important; border: 1px solid %s !important;}
        .stButton button {background-color: %s !important; color: %s !important; border: 1px solid %s !important;}
        .message {padding: 12px 16px; margin: 8px 0; border-radius: 15px; max-width: 80%%; animation: fadeIn 0.3s ease-in;}
        .user-message {background: %s; color: %s; margin-left: auto;}
        .assistant-message {background: %s; color: %s; margin-right: auto;}
        @keyframes fadeIn {from {opacity:0; transform:translateY(20px);} to {opacity:1; transform:translateY(0);}}
        @media (max-width: 600px) {.message {max-width: 90%%; padding: 10px 12px; font-size: 14px;} .stChatFloatingInputContainer {padding: 0.5rem;}}
    </style>
    """
    if st.session_state.dark_mode:
        st.markdown(theme % (
            "#1a1a1a", "#ffffff",
            "#2d2d2d", "#ffffff",
            "#2d2d2d",
            "#ffffff", "#404040", "#555555",
            "#4CAF50", "#ffffff", "#4CAF50",
            "#004456", "#ffffff",
            "#2d3b2d", "#ffffff"
        ), unsafe_allow_html=True)
    else:
        st.markdown(theme % (
            "#ffffff", "#333333",
            "#f0f2f6", "#333333",
            "#ffffff",
            "#333333", "#ffffff", "#cccccc",
            "#4CAF50", "#ffffff", "#4CAF50",
            "#005f73", "#ffffff",
            "#e8f5e9", "#333333"
        ), unsafe_allow_html=True)

apply_theme()

# ----------------- LOGIN / REGISTER -----------------
if st.session_state.token is None:
    if st.session_state.page == "login":
        st.markdown("""
        <div style="
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            color: #ffffff;
        ">
        <h2 style='text-align:center;'>🔐 Login</h2>
        <p style='text-align:center;font-size:14px;'>Enter your credentials to access the assistant</p>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", key="login_email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

        if st.button("Login", key="login_btn"):
            token = login(email, password)
            if token:
                st.session_state.token = token
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

        if st.button("Go to Register", key="to_register"):
            st.session_state.page = "register"
            st.rerun()

    elif st.session_state.page == "register":
        st.markdown("""
        <div style="
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: linear-gradient(135deg, #fddb92 0%, #d1fdff 100%);
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            color: #333333;
        ">
        <h2 style='text-align:center;'>📝 Register</h2>
        <p style='text-align:center;font-size:14px;'>Create a new account to start chatting</p>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", key="reg_user", placeholder="Choose a username")
        email = st.text_input("Email", key="reg_email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", key="reg_pass", placeholder="Enter a password")

        if st.button("Register", key="register_btn"):
            res = register(username, email, password)
            if res.status_code == 201:
                st.success("🎉 Account created! Please login.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(f"Registration failed: {res.text}")

        if st.button("Back to Login", key="back_login"):
            st.session_state.page = "login"
            st.rerun()

# ----------------- MAIN APP (AFTER LOGIN) -----------------
else:
    # Header
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.title("💬 GenAI Assistant 🤖")
        st.caption("🚀 Powered by Google Gemini 🌐 | Created by [Suraj Badre 🙏](https://github.com/badre-suraj-23)")
    with header_col2:
        st.markdown("""
        <div style="text-align: right; margin-top: 15px;">
            <a href="https://www.linkedin.com/in/suraj-badre/" target="_blank">
                <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
            </a>
        </div>
        """, unsafe_allow_html=True)

    # Logout
    if st.sidebar.button("🚪 Logout"):
        st.session_state.token = None
        st.session_state.page = "login"
        st.session_state.messages = []
        st.rerun()

    # Chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f'<div class="message {message["role"]}-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Input
    col1, col2 = st.columns([6, 1])
    with col1:
        prompt = st.text_input("Type your message here...", label_visibility="collapsed", key="input_field", placeholder="Ask me anything")
    with col2:
        generate = st.button("Generate", key="generate_btn")

    if generate and prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f'<div class="message user-message">{prompt}</div>', unsafe_allow_html=True)
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                response = chain.invoke({"question": prompt})
                st.markdown(f'<div class="message assistant-message">{response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # ✅ Clear input field after generating response
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
        for example in ["Explain quantum computing in simple terms", "How do I make a HTTP request in Python?", "What's the difference between AI and ML?", "Suggest healthy breakfast ideas"]:
            if st.button(example, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()

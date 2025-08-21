import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time

# ----------------- CONFIGURATION -----------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ----------------- DEMO AUTHENTICATION -----------------
def login(email, password):
    # Simple demo authentication - in a real app, use proper auth
    if email and password:  # Very basic validation
        return "demo_token"
    return None

def register(username, email, password):
    # Demo registration - in a real app, use proper registration
    if username and email and password:
        class DummyResponse:
            status_code = 201
            text = "Account created"
        return DummyResponse()
    return None

# ----------------- SESSION INIT -----------------
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "token" not in st.session_state:
        st.session_state.token = None
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "processing" not in st.session_state:
        st.session_state.processing = False

init_session_state()

# ----------------- LLM INIT -----------------
@st.cache_resource
def load_chain():
    if not GOOGLE_API_KEY:
        st.error("GOOGLE_API_KEY is missing! Please check your .env file.")
        return None
        
    try:
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
    except Exception as e:
        st.error(f"Error initializing AI model: {str(e)}")
        return None

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
        .footer {position: fixed; bottom: 10px; left: 0; right: 0; text-align: center; color: %s; font-size: 0.8rem;}
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
            "#2d3b2d", "#ffffff",
            "#888888"
        ), unsafe_allow_html=True)
    else:
        st.markdown(theme % (
            "#ffffff", "#333333",
            "#f0f2f6", "#333333",
            "#ffffff",
            "#333333", "#ffffff", "#cccccc",
            "#4CAF50", "#ffffff", "#4CAF50",
            "#005f73", "#ffffff",
            "#e8f5e9", "#333333",
            "#666666"
        ), unsafe_allow_html=True)

apply_theme()

# ----------------- AUTH PAGES -----------------
def show_login():
    st.markdown("<h2 style='text-align:center;'>🔐 Login</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                token = login(email, password)
                if token:
                    st.session_state.token = token
                    st.session_state.page = "main"
                    st.success("Demo login successful!")
                    time.sleep(0.5)  # Brief delay for smoother transition
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    st.markdown("<div style='text-align:center; margin-top:20px;'>Don't have an account? </div>", unsafe_allow_html=True)
    if st.button("Register", use_container_width=True, key="go_to_register"):
        st.session_state.page = "register"
        st.rerun()

def show_register():
    st.markdown("<h2 style='text-align:center;'>📝 Register</h2>", unsafe_allow_html=True)
    
    with st.form("register_form"):
        username = st.text_input("Username", key="reg_user")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_pass")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not all([username, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                res = register(username, email, password)
                if res and res.status_code == 201:
                    st.success("Demo account created! Please login.")
                    st.session_state.page = "login"
                    time.sleep(1)  # Brief delay for smoother transition
                    st.rerun()
                else:
                    st.error("Registration failed")
    
    if st.button("Back to Login", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()

# ----------------- MAIN APP -----------------
def show_main_app():
    # Header
    header_col1, header_col2 = st.columns([6, 1])
    with header_col1:
        st.title("🧠 LangChain + GenAI 🤖")
    with header_col2:
        st.markdown("""
        <div style="text-align: right; margin-top: 15px;">
            <a href="https://www.linkedin.com/in/YOUR-LINKEDIN-USERNAME" target="_blank">
                <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" width="100">
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
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
            "Explain quantum computing",
            "How do I make a HTTP request in Python?",
            "Difference between AI and ML",
            "Suggest healthy breakfast ideas"
        ]
        
        for example in examples:
            if st.button(example, use_container_width=True, key=f"example_{example}"):
                if not st.session_state.processing:
                    process_user_input(example)
        
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.page = "login"
            st.session_state.messages = []
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f'<div class="message {message["role"]}-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    if not st.session_state.processing:
        if prompt := st.chat_input("Type your message here..."):
            process_user_input(prompt)
    else:
        st.chat_input("Processing...", disabled=True)
    
    # Footer
    st.markdown('<div class="footer">Powered by LangChain & Gemini AI</div>', unsafe_allow_html=True)

def process_user_input(prompt):
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(f'<div class="message user-message">{prompt}</div>', unsafe_allow_html=True)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown('<div class="message assistant-message">🤖 Thinking...</div>', unsafe_allow_html=True)
        
        try:
            if chain:
                response = chain.invoke({"question": prompt})
                message_placeholder.markdown(f'<div class="message assistant-message">{response}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                message_placeholder.markdown('<div class="message assistant-message">❌ AI model not available</div>', unsafe_allow_html=True)
        except Exception as e:
            message_placeholder.markdown(f'<div class="message assistant-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
    
    st.session_state.processing = False
    st.rerun()

# ----------------- APP FLOW -----------------
if st.session_state.token is None:
    if st.session_state.page == "login":
        show_login()
    elif st.session_state.page == "register":
        show_register()
else:
    show_main_app()
import streamlit as st 

from agent_management import display_agents
from ui_utils import get_api_key, display_api_key_input, display_discussion_and_whiteboard, display_download_button, display_user_input, display_rephrased_request, display_reset_and_upload_buttons, display_user_request_input

def main(): 
    initialize_session_state()
    setup_page_layout()
    manage_api_key()
    handle_model_selection()
    render_main_interface()

def initialize_session_state():
    """ Initialize or reset important session state variables. """
    if "discussion" not in st.session_state:
        st.session_state.discussion = ""
    if "whiteboard" not in st.session_state:
        st.session_state.whiteboard = ""

def setup_page_layout():
    """ Apply custom CSS to the Streamlit page. """
    st.markdown(load_css(), unsafe_allow_html=True)

def load_css():
    """ Returns the CSS for the Streamlit page as a string. """
    return """
        <style>
        /* General styles */
        body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
        .sidebar .sidebar-content { background-color: #ffffff; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
        .sidebar .st-emotion-cache-k7vsyb h1, .sidebar h2 { font-size: 12px; font-weight: bold; color: #007bff; }
        .sidebar .stButton button { width: 100%; padding: 10px; background-color: #007bff; color: white; border-radius: 5px; transition: background-color 0.3s; }
        .sidebar .stButton button:hover { background-color: #0056b3; }
        .main .stTextInput input, .main .stTextArea textarea { width: 100%; padding: 10px; border: 1px solid #cccccc; border-radius: 5px; }
        .main .stButton button { background-color: #dc3545; color: white; border-radius: 5px; transition: background-color 0.3s; }
        .main .stButton button:hover { background-color: #c82333; }
        .main h1 { font-size: 32px; color: #007bff; }
        .main .stSelectbox select { width: 100%; padding: 10px; border-radius: 5px; }
        .main .stAlert { color: #dc3545; }
        </style>
    """

def manage_api_key():
    """ Manage API key input and validation. """
    api_key = get_api_key()
    if api_key is None:
        api_key = display_api_key_input()
        if api_key is None:
            st.warning("Please enter your GROQ_API_KEY to use the app.")
            return

def handle_model_selection():
    """ Handle model selection and configuration. """
    model_token_limits = {
        'llama3-70b-8192': 8192, 'llama3-8b-8192': 8192, 'mixtral-8x7b-32768': 32768, 'gemma-7b-it': 8192
    }
    col1, col2, col3 = st.columns([2, 5, 3])
    with col3:
        selected_model = st.selectbox('Select Model', options=list(model_token_limits.keys()), index=0, key='model_selection')
        st.session_state.model = selected_model
        st.session_state.max_tokens = model_token_limits[selected_model]
        st.session_state.temperature = st.slider("Set Temperature", 0.0, 1.0, st.session_state.get('temperature', 0.3), 0.01, 'temperature')

def render_main_interface():
    """ Render the main interface of the application. """
    st.title("AutoGroq")
    with st.sidebar:
        display_agents()
    with st.container():
        display_user_request_input()
        display_rephrased_request()
        display_discussion_and_whiteboard()
        display_user_input()
        display_reset_and_upload_buttons()
    display_download_button()

if __name__ == "__main__": 
    main()
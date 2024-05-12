import base64
import os
import re
import requests
from bs4 import BeautifulSoup
import streamlit as st

from api_utils import send_request_to_groq_api               
from ui_utils import get_api_key, update_discussion_and_whiteboard

def agent_button_callback(agent_index):
    def callback():
        st.session_state['selected_agent_index'] = agent_index
        agent = st.session_state.agents[agent_index]
        agent_name = agent['config'].get('name', '')
        st.session_state['form_agent_name'] = agent_name
        st.session_state['form_agent_description'] = agent.get('description', '')
        process_agent_interaction(agent_index)
    return callback

def construct_request(agent_name, description, user_request, user_input, rephrased_request, reference_url):
    request = f"Act as the {agent_name} who {description}."
    additional_details = [f"Original request was: {user_request}" if user_request else "",
                          f"You are helping a team work on satisfying {rephrased_request}." if rephrased_request else "",
                          f"Additional input: {user_input}." if user_input else "",
                          fetch_url_content(reference_url) if reference_url else ""]
    request += " ".join(filter(None, additional_details))
    if st.session_state.discussion:
        request += f" The discussion so far has been {st.session_state.discussion[-50000:]}."
    return request

def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return f"Reference URL content: {soup.get_text()}."
    except requests.exceptions.RequestException as e:
        return f"Error occurred while retrieving content from {url}: {e}"

def delete_agent(index):
    if 0 <= index < len(st.session_state.agents):
        agent = st.session_state.agents[index]
        expert_name = agent["expert_name"]
        del st.session_state.agents[index]
        json_file = json_file_path(expert_name)
        try:
            os.remove(json_file)
            st.success(f"JSON file deleted: {json_file}")
        except OSError:
            st.error(f"JSON file not found: {json_file}")
        st.experimental_rerun()

def display_agents():
    if "agents" in st.session_state and st.session_state.agents:
        st.sidebar.title("Your Agents")
        st.sidebar.subheader("Click to interact")
        for index, agent in enumerate(st.session_state.agents):
            display_agent_button(agent, index)
        if st.session_state.get('show_edit'):
            display_agent_edit_form()
    else:
        st.sidebar.warning("No agents have yet been created. Please enter a new request.")

def display_agent_button(agent, index):
    agent_name = agent["config"].get("name", f"Unnamed Agent {index + 1}")
    col1, col2 = st.sidebar.columns([1, 4])
    with col1:
        if st.button("⚙️", key=f"gear_{index}"):
            st.session_state['edit_agent_index'] = index
            st.session_state['show_edit'] = True
    with col2:
        if st.button(agent_name, key=f"agent_{index}", on_click=agent_button_callback(index)):
            st.session_state['next_agent'] = agent_name

def display_agent_edit_form():
    edit_index = st.session_state.get('edit_agent_index')
    if edit_index is not None and 0 <= edit_index < len(st.session_state.agents):
        agent = st.session_state.agents[edit_index]
        with st.expander(f"Edit Properties of {agent['config'].get('name', '')}", expanded=True):
            new_name = st.text_input("Name", value=agent['config'].get('name', ''), key=f"name_{edit_index}")
            new_description = st.text_area("Description", value=agent.get('description', ''), key=f"desc_{edit_index}")
            if st.button("Save Changes", key=f"save_{edit_index}"):
                save_agent_changes(agent, new_name, new_description)
                st.experimental_rerun()

def save_agent_changes(agent, new_name, new_description):
    agent['config']['name'] = new_name
    agent['description'] = new_description
    st.success("Agent properties updated!")
    st.session_state.pop('show_edit', None)
    st.session_state.pop('edit_agent_index', None)

def json_file_path(expert_name):
    safe_name = re.sub(r'[^a-zA-Z0-9\s]', '', expert_name).lower().replace(' ', '_')
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "agents"))
    return os.path.join(agents_dir, f"{safe_name}.json")

def process_agent_interaction(agent_index):
    agent = st.session_state.agents[agent_index]
    request = construct_request(agent['config'].get('name', ''), agent.get('description', ''),
                                st.session_state.get('user_request', ''), st.session_state.get('user_input', ''),
                                st.session_state.get('rephrased_request', ''), st.session_state.get('reference_url', ''))
    response = send_request(agent['config'].get('name', ''), request)
    if response:
        update_discussion_and_whiteboard(agent['config'].get('name', ''), response, st.session_state.get('user_input', ''))
        st.session_state['selected_agent_index'] = agent_index

def send_request(agent_name, request):
    api_key = get_api_key()
    if not api_key:
        st.error("API key not found. Please enter your API key.")
        return None
    return send_request_to_groq_api(agent_name, request, api_key)

import requests
import streamlit as st
import time

def make_api_request(url, data, headers):
    """Make an API request while managing rate limits and handling common errors."""
    time.sleep(2)  # Throttle requests to ensure at least 2 seconds between calls.
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raises exception for HTTP errors.
        return response.json()
    except requests.exceptions.HTTPError as e:
        handle_http_error(response)
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def handle_http_error(response):
    """Handle different types of HTTP errors with appropriate user feedback."""
    if response.status_code == 429:
        error_message = response.json().get("error", {}).get("message", "No error message provided.")
        st.error(f"Rate limit reached. Please try again later. Error details: {error_message}")
    else:
        st.error(f"API request failed with status {response.status_code}. Response: {response.text}")

def prepare_headers(api_key):
    """Prepare headers for the API request, ensuring the API key is included."""
    if not api_key:
        raise ValueError("API key not found. Please enter your API key.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def send_request_to_groq_api(expert_name, request, api_key):
    """Send a formatted request to the Groq API and handle the response."""
    if api_key is None:
        api_key = st.session_state.get('api_key')
        if not api_key:
            st.error("API key not found. Please enter your API key.")
            return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    data = create_request_data(request)
    headers = prepare_headers(api_key)

    response = make_api_request(url, data, headers)
    return parse_response(response)

def create_request_data(request):
    """Create the data payload for the API request based on the session state."""
    return {
        "model": st.session_state.get('model'),
        "temperature": st.session_state.get('temperature', 0.1),
        "max_tokens": st.session_state.get('max_tokens', 1000),
        "top_p": 1,
        "stop": "TERMINATE",
        "messages": [
            {"role": "system", "content": "You are a chatbot capable of anything and everything."},
            {"role": "user", "content": request}
        ]
    }

def parse_response(response):
    """Parse the API response and extract the required information."""
    if response and "choices" in response and response["choices"]:
        return response["choices"][0].get("message", {}).get("content")
    st.error("Unexpected response format from the Groq API.")
    return None

if __name__ == "__main__":
    st.set_page_config(page_title="Streamlit Groq API Example")
    try:
        response = send_request_to_groq_api("Example Expert", "How does the GROQ model work?", "your_api_key_here")
        if response:
            st.write("Response from Groq API:", response)
    except ValueError as e:
        st.error(str(e))
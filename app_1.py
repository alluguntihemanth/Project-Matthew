import streamlit as st
from conv_agent import load_conv_agent, handle_chat
from google_fit_api import authenticate_user, fetch_heart_rate_data

def main():
    st.title("Chat with Matthew!")

    # Display the logo
    st.image('chatbot-saying-hi.png')

    # Step for user authentication
    if 'credentials' not in st.session_state:
        st.write("Please authenticate your Google account to access heart rate data.")
        auth_url = authenticate_user()
        st.markdown(f"[Authorize Here]({auth_url})")  # Display the authorization link

        redirect_url = st.text_input("Paste the full redirect URL here:")
        if redirect_url:
            # Exchange the authorization code for credentials
            flow = st.session_state.flow
            flow.fetch_token(authorization_response=redirect_url)
            creds = flow.credentials
            st.session_state.credentials = creds
            st.success("Authentication successful!")
    else:
        creds = st.session_state.credentials
        st.success("You are authenticated.")

        # Initialize the Groq client
        groq_api_key = st.secrets["groq"]["api_key"]
        groq_chat, memory, system_prompt = load_conv_agent(groq_api_key)

        # Fetch heart rate data
        heart_rate_data = fetch_heart_rate_data(creds)
        current_heart_rate = heart_rate_data[-1]["heart_rate"] if heart_rate_data else None
        
        # Handle the conversation
        handle_chat(groq_chat, memory, system_prompt, current_heart_rate)

if __name__ == "__main__":
    main()


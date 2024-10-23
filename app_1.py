import streamlit as st
from conv_agent import load_conv_agent, handle_chat
from google_fit_api import authenticate_user, fetch_heart_rate_data
import datetime

def main():
    # Display the logo and the title of the application
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('chatbot-saying-hi.png')
    st.title("Chat with Matthew!")

    # Initialize the Google Fit API and Groq client
    # Application initialization code...
    creds = authenticate_user()
    if not creds:
        st.stop()  # Stop execution if authentication fails
    groq_api_key = st.secrets["groq"]["api_key"]
    
    # Load the conversational agent
    groq_chat, memory, system_prompt = load_conv_agent(groq_api_key)

    current_heart_rate = None
    if creds:
        # Fetch heart rate data
        heart_rate_data = fetch_heart_rate_data(creds)
        if heart_rate_data:
            # Remove or comment out this line to hide heart rate data
            # st.write("Heart rate data:", heart_rate_data)

            # Extract the latest heart rate value
            current_heart_rate = heart_rate_data[-1]["heart_rate"]  # Latest data point
        else:
            st.write("No heart rate data available.")
    
    # Handle the conversation, passing heart rate data
    handle_chat(groq_chat, memory, system_prompt, current_heart_rate)

if __name__ == "__main__":
    main()


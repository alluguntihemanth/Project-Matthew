import os
import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import time

def authenticate_user():
    flow = Flow.from_client_secrets_file(
        'credentials/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/fitness.heart_rate.read'],
        redirect_uri='https://project-matthew-hemanthallugunti.streamlit.app/'  # Use your app's deployed URL
    )

    if 'credentials' in st.session_state:
        return st.session_state['credentials']

    # Check for authorization code in query params
    query_params = st.query_params()
    
    if 'code' in query_params:
        code = query_params['code'][0]  # Make sure to extract the code correctly
        flow.fetch_token(authorization_response=f"https://project-matthew-hemanthallugunti.streamlit.app/?code={code}")
        creds = flow.credentials
        st.session_state['credentials'] = creds
        return creds
    else:
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        st.write(f'Please authorize the application: [Authorize Here]({auth_url})')

    return None



def authenticate_user():
    flow = Flow.from_client_secrets_file(
        'credentials/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/fitness.heart_rate.read'],
        redirect_uri='https://project-matthew-hemanthallugunti.streamlit.app/'  # Use your app's deployed URL
    )

    if 'credentials' in st.session_state:
        return st.session_state['credentials']

    # Check for authorization code in query params
    query_params = st.query_params()
    
    if 'code' in query_params:
        code = query_params['code'][0]  # Make sure to extract the code correctly
        flow.fetch_token(authorization_response=f"https://project-matthew-hemanthallugunti.streamlit.app/?code={code}")
        creds = flow.credentials
        st.session_state['credentials'] = creds
        return creds
    else:
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        st.write(f'Please authorize the application: [Authorize Here]({auth_url})')

    return None


# Main function to handle app logic
def main():
    creds = authenticate_user()
    if creds:
        heart_rate_data = fetch_heart_rate_data(creds)
        if heart_rate_data:
            st.write(heart_rate_data)
        else:
            st.write("No heart rate data found.")
    else:
        st.write("Please authorize access to your Google Fit data.")

if __name__ == '__main__':
    main()



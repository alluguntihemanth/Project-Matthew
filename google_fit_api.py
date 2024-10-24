import os
import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import time

def authenticate_user():
    """Authenticates the user and stores credentials in session state."""
    flow = Flow.from_client_secrets_file(
        'credentials/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/fitness.heart_rate.read'],
        redirect_uri='https://project-matthew-hemanthallugunti.streamlit.app/'  # Update with your app's URL
    )

    # Check if credentials are already stored
    if 'credentials' in st.session_state:
        st.write("Using existing credentials...")
        return st.session_state['credentials']

    # Access query parameters from the app's URL
    query_params = st.query_params.to_dict()  # Use the new method

    if 'code' in query_params:
        # Handle the token exchange with the authorization code
        code = query_params['code']  # This is already a string
        flow.fetch_token(authorization_response=f"https://project-matthew-hemanthallugunti.streamlit.app/?code={code}")
        creds = flow.credentials
        st.session_state['credentials'] = creds  # Store in session state
        st.write("New credentials acquired.")
        return creds
    else:
        # Generate and display the authorization link
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        st.markdown(f'[Authorize Here]({auth_url})')  # Markdown for cleaner link display

    return None

def fetch_heart_rate_data(creds):
    """Fetches heart rate data from Google Fit API using the provided credentials."""
    service = build('fitness', 'v1', credentials=creds)

    # Get available data sources
    data_sources = service.users().dataSources().list(userId='me').execute()
    heart_rate_source = None

    # Find the heart rate data source
    for data_source in data_sources.get('dataSource', []):
        if 'com.google.heart_rate.bpm' in data_source['dataStreamId']:
            heart_rate_source = data_source
            break

    if heart_rate_source:
        # Fetch heart rate data from the identified source
        dataset_id = f"0-{int(time.time() * 1000000000)}"
        dataset = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=heart_rate_source['dataStreamId'],
            datasetId=dataset_id
        ).execute()

        # Extract and return heart rate points
        if 'point' in dataset:
            heart_rate_data = [
                {
                    'start_time': point['startTimeNanos'],
                    'end_time': point['endTimeNanos'],
                    'heart_rate': point['value'][0]['fpVal']
                }
                for point in dataset['point']
            ]
            return heart_rate_data

    return None

def main():
    """Main function to manage app logic."""
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

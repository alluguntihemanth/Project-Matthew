import os
import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import time

def authenticate_user():
    st.write("Starting user authentication...")  # Debug line
    flow = Flow.from_client_secrets_file(
        'credentials/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/fitness.heart_rate.read'],
        redirect_uri='https://project-matthew-hemanthallugunti.streamlit.app/'
    )

    if 'credentials' in st.session_state:
        st.write("Using existing credentials...")  # Debug line
        return st.session_state['credentials']

    # Check for authorization code in query params
    query_params = st.query_params()
    st.write("Query parameters:", query_params)  # Debug line
    
    if 'code' in query_params:
        code = query_params['code'][0]
        flow.fetch_token(authorization_response=f"https://project-matthew-hemanthallugunti.streamlit.app/?code={code}")
        creds = flow.credentials
        st.session_state['credentials'] = creds
        st.write("New credentials acquired.")  # Debug line
        return creds
    else:
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        st.write(f'Please authorize the application: [Authorize Here]({auth_url})')
        return None




def fetch_heart_rate_data(creds):
    """Fetches heart rate data from Google Fit API using user credentials."""
    service = build('fitness', 'v1', credentials=creds)

    # Fetch heart rate data
    data_sources = service.users().dataSources().list(userId='me').execute()
    heart_rate_source = None

    for data_source in data_sources['dataSource']:
        if 'com.google.heart_rate.bpm' in data_source['dataStreamId']:
            heart_rate_source = data_source
            break

    if heart_rate_source:
        dataset = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=heart_rate_source['dataStreamId'],
            datasetId="0-{}".format(int(time.time() * 1000000000))
        ).execute()

        if 'point' in dataset:
            heart_rate_data = []
            for point in dataset['point']:
                heart_rate_data.append({
                    'start_time': point['startTimeNanos'],
                    'end_time': point['endTimeNanos'],
                    'heart_rate': point['value'][0]['fpVal']
                })
            return heart_rate_data
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



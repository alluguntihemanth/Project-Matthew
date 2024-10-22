import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
import time

def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/fitness.heart_rate.read'],
    )
    
    # Ensure this matches Google Cloud Console
    redirect_uri = 'https://project-matthew-hemanthallugunti.streamlit.app/'  

    # Specify access_type and redirect_uri explicitly
    auth_url, _ = flow.authorization_url(access_type='offline', redirect_uri=redirect_uri)
    st.write(f'Please authorize the application: [Authorize Here]({auth_url})')

    # Check for the 'code' in query parameters
    if 'code' in st.experimental_get_query_params():
        flow.fetch_token(authorization_response=st.experimental_get_query_params()['code'][0])
        creds = flow.credentials
        st.session_state.credentials = creds
        return creds

    return None



def fetch_heart_rate_data(creds):
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



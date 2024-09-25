import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import requests
from googleapiclient.discovery import build
import time

def authenticate_user():
    scopes = ["https://www.googleapis.com/auth/fitness.heart_rate.read"]

    # Check if user has already authenticated
    if 'credentials' not in st.session_state:
        client_secrets_path = os.path.join('credentials', 'client_secrets.json')

        # Debug print to verify the path
        print("Client secrets path:", client_secrets_path)
        
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes=scopes)
        creds = flow.run_local_server(port=8504)  # Use the same port each time

        st.session_state.credentials = creds

    return st.session_state.credentials

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

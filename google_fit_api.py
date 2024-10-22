import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import requests
from googleapiclient.discovery import build
import time

def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/fitness.heart_rate.read']
    )

    # Get the authorization URL
    auth_url, _ = flow.authorization_url(access_type='offline')
    
    st.write("Please go to this URL to authorize the application:")
    st.markdown(f"[Authorize Here]({auth_url})")  # Link for the user to click

    # Ask for the authorization response URL
    redirect_response = st.text_input("Paste the full redirect URL here:")

    if redirect_response:
        # Exchange the authorization code for credentials
        flow.fetch_token(authorization_response=redirect_response)
        creds = flow.credentials
        st.session_state.credentials = creds
        return st.session_state.credentials

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


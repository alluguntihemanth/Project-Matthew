import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import requests
from googleapiclient.discovery import build
import time


def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',  # Your OAuth client secrets file
        scopes=['https://www.googleapis.com/auth/fitness.heart_rate.read']  # Example scope
    )

    # Instead of running a local server, use the console flow
    creds = flow.run_console()  # This will prompt the user to visit a URL and enter a code
    return creds

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

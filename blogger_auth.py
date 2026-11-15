import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def connect_blogger():
    creds = None

    if os.path.exists("token.json"):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(
                host="127.0.0.1",
                port=8080,
                open_browser=False
            )

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("blogger", "v3", credentials=creds)
    print("تم الاتصال بحساب Blogger بنجاح!")
    return service

if __name__ == "__main__":
    connect_blogger()

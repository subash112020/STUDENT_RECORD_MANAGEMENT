import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():

    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


if __name__ == "__main__":
    service = get_gmail_service()
    print("running succesfully")

def get_latest_client_reply(service, client_email):

    result = service.users().messages().list(
        userId="me",
        q=f"from:{client_email}"
    ).execute()

    messages = result.get("messages", [])

    if not messages:
        return None

    latest_message = messages[0]

    return latest_message["id"]

#!/usr/bin/env python3

import datetime
import webbrowser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import sys
import os
import os.path

# If modifying these SCOPES, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    """Authenticate and return the Google Calendar service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def get_all_calendars(service):
    """Retrieve all calendars the user has access to."""
    calendar_list = service.calendarList().list().execute()
    return [calendar['id'] for calendar in calendar_list.get('items', [])]


def get_next_event(service, calendar_ids):
    """Retrieve the next upcoming event across all calendars."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    closest_event = None
    for calendar_id in calendar_ids:
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime', eventTypes='default').execute()
        events = events_result.get('items', [])
        if events:
            event = events[0]
            if 'dateTime' in event['start']:
                if (closest_event is None or
                    event['start']['dateTime'] < closest_event['start']['dateTime']):
                    closest_event = event
    return closest_event

def extract_meet_link(event):
    """Extract Google Meet link from an event."""
    if 'hangoutLink' in event:
        return event['hangoutLink']
    # Check for Meet link in the event description or location (fallback)
    if 'description' in event and 'https://meet.google.com/' in event['description']:
        return [word for word in event['description'].split() if 'https://meet.google.com/' in word][0]
    if 'location' in event and 'https://meet.google.com/' in event['location']:
        return event['location']
    return None

def main():
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    service = authenticate_google_calendar()
    # Get all calendar IDs
    calendar_ids = get_all_calendars(service)
    print(f"Found {len(calendar_ids)} calendars.")

    # Get the next event across all calendars
    event = get_next_event(service, calendar_ids)
    if event:
        print(f"Next event: {event['summary']} at {event['start']['dateTime']}")
        meet_link = extract_meet_link(event)
        if meet_link:
            print(f"Opening Google Meet link: {meet_link}")
            webbrowser.open_new_tab(meet_link)
        else:
            print("No Google Meet link found for the next event.")

if __name__ == '__main__':
    main()


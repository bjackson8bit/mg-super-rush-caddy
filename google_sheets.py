from __future__ import print_function
from pprint import pprint
import os.path
from scripts.utils.event_logging import OutputConn
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

from six import viewvalues

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
def create_sheet(sheet_name, creds_filename):
    creds = check_creds(creds_filename)
    if not creds:
        return None
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet_body = {
        'properties': {
            'title': sheet_name
        }
    }
    request = service.spreadsheets().create(body=sheet_body)
    response = request.execute()

    return response['spreadsheetId']

def check_creds(creds_filename):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    token_filename = 'token.json'
    token_file = os.path.join(os.path.dirname(creds_filename), token_filename)
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_filename, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        return creds
    except Exception:
        return None

# pprint(create_sheet('test_create_sheet', './credentials.json'))

    # # Call the Sheets API
    # sheet_body = {
    #     'properties': {
    #         'title': 'Golf'
    #     }
    # }
    # request = service.spreadsheets().create(body=sheet_body)
    # response = request.execute()

    # pprint(response)

    # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                             range=SAMPLE_RANGE_NAME).execute()
    # values = result.get('values', [])

    # if not values:
    #     print('No data found.')
    # else:
    #     print('Name, Major:')
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         print('%s, %s' % (row[0], row[4]))

def get_sheet_from_id(sheet_id, creds_filename):
    creds = check_creds(creds_filename)
    if not creds:
        return None

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range='A2:E').execute()
        values = result.get('values', [])

        if not values:
            print('No data found in sheet.')
        else:
            print('Found data in sheet')
        return True
    except Exception:
        return None

def create_sheets_connection(creds_filename):
    creds = check_creds(creds_filename)
    if not creds:
        return None

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        return sheet
    except Exception:
        return None


class SheetsOutputConn(OutputConn):
    def __init__(self, creds_filename, sheet_id, init_col, init_row) -> None:
        self.sheet = create_sheets_connection(creds_filename)
        if not self.sheet:
            print("Error initializing ActiveSheetsConn")
        self.init_col = init_col
        self.init_row = init_row
        self.sheet_id = sheet_id

    def write_rows(self, row_data):
        value_input_option='RAW'
        end_row = str(int(self.init_row) + len(row_data))
        range=f"{self.init_col}{self.init_row}:{end_row}"
        value_body = {
            "range": range,
            "majorDimension": "ROWS",
            "values": row_data
        }
        try:
            request = self.sheet.values().update(spreadsheetId=self.sheet_id, range=range, valueInputOption=value_input_option, body=value_body)
            response = request.execute()
            if response:
                print(f"Successfully wrote data to Google sheets")
            else:
                print(f"Failed to write Google sheet data to {self.sheet_id}")
        except Exception:
            print(f"Failed to write Google sheet data to {self.sheet_id}")
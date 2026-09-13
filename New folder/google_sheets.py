import os
import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICE_ACCOUNT_FILE = os.path.join(
    BASE_DIR,
    "google_service_account.json"
)

SPREADSHEET_NAME = "Oak & Ember Enquiries_AnimeshDeb"
WORKSHEET_NAME = "Enquiries"


def get_sheet():

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(
        SPREADSHEET_NAME
    )

    worksheet = spreadsheet.worksheet(
        WORKSHEET_NAME
    )

    return worksheet


def store_enquiry(enquiry):

    worksheet = get_sheet()

    worksheet.append_row([
        enquiry.get("timestamp", ""),
        enquiry.get("source", ""),
        enquiry.get("name", ""),
        enquiry.get("email", ""),
        enquiry.get("contact", ""),
        enquiry.get("category", ""),
        enquiry.get("budget", ""),
        enquiry.get("query", ""),
        enquiry.get("product_ids", ""),
        enquiry.get("thread_id", "")
    ])
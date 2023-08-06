import os
from dotenv import load_dotenv

load_dotenv()

google = {
    "spreadsheetid": os.getenv("GOOGLE_SPREADSHEET_ID"),
    "credentialsfile": os.getenv("GOOGLE_AUTH_FILENAME", "key.json"),
    "defaultsheet": os.getenv("GOOGLE_SHEETNAME", "to_download"),
    "scopes": ['https://www.googleapis.com/auth/spreadsheets']
}

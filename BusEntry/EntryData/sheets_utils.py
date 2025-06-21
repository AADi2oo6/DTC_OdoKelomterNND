import gspread
from google.oauth2.service_account import Credentials
import os

# --- CONFIGURATION ---
SPREADSHEET_ID = '1I-FGojh10I-BO4_jwbsXX6vhB_iKOnpZTvM261SQIJk'
CREDENTIALS_FILENAME = 'credentials.json'
# ----------------------

def get_authenticated_client():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(
        os.path.join(current_dir, CREDENTIALS_FILENAME),
        scopes=scopes
    )
    return gspread.authorize(creds)

def append_to_sheet(data):
    client = get_authenticated_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.sheet1
    worksheet.append_row(data)

def update_in_sheet(data):
    client = get_authenticated_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.sheet1

    try:
        cell = worksheet.find(str(data['id']), in_column=12)
        if cell:
            row_values = [
            data['date'],
            data['shift'],
            data['bus_no'],
            data['out_kms'],
            data['in_kms'],
            data['diff'],
            data['soc'],
            data['soc_in'],
            data['time'],
            data['user'],
            data['in_time']
            ]
            worksheet.update(f'A{cell.row}:K{cell.row}', [row_values])
            return True
        return False
    except gspread.CellNotFound:  # CORRECTED EXCEPTION
        print(f"Entry with ID {data['id']} not found in sheet")
        return False
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return False
import gspread
from google.oauth2.service_account import Credentials
import os
from gspread.exceptions import WorksheetNotFound

# --- CONFIGURATION ---
SPREADSHEET_ID = '1I-FGojh10I-BO4_jwbsXX6vhB_iKOnpZTvM261SQIJk'
CREDENTIALS_FILENAME = 'credentials.json'
# ----------------------

def get_authenticated_client():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(
        os.path.join(current_dir, CREDENTIALS_FILENAME),
        scopes=scopes
    )
    return gspread.authorize(creds)

def append_to_sheet(data):
    client = get_authenticated_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.sheet1
    worksheet.append_row(data)

def update_in_sheet(data):
    """
    Updates an existing row in the Google Sheet by matching date, bus_no, and shift.
    Assumes columns:
    A: date, B: shift, C: bus_no, D: out_kms, E: in_kms, F: diff, G: soc, H: soc_in, I: time, J: user
    """
    client = get_authenticated_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.sheet1

    try:
        all_rows = worksheet.get_all_values()
        # Find the row index (1-based) where date, shift, and bus_no all match
        row_index = None
        for idx, row in enumerate(all_rows, start=1):
            # Ensure row has at least 3 columns to avoid IndexError
            if len(row) >= 3:
                if (
                    row[0] == data['date'] and
                    row[1] == data['shift'] and
                    row[2] == data['bus_no']
                ):
                    row_index = idx
                    break

        if row_index:
            row_values = [
                data['date'],
                data['shift'],
                data['bus_no'],
                data['out_kms'],
                data['in_kms'],
                data['diff'],
                data['soc'],
                data['soc_in'],
                data['time'],
                data['user'],
                data['in_time']
            ]
            worksheet.update(f'A{row_index}:k{row_index}', [row_values])
            return True
        else:
            print(f"Entry with date={data['date']}, shift={data['shift']}, bus_no={data['bus_no']} not found in sheet")
            return False
    except WorksheetNotFound:
        print("Worksheet not found.")
        return False
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return False

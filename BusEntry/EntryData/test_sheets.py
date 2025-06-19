# test_sheets.py
from sheets_utils import update_in_sheet

test_data = {
    'date': '2025-06-19',
    'shift': 'Evening',
    'bus_no': '6900',
    'out_kms': '100.5',
    'in_kms': '150.2',
    'diff': '49.7',
    'soc': '80%',
    'soc_in': '60%',
    'time': '14:30',
    'user': 'test_user'
}

if update_in_sheet(test_data):
    print("Update successful!")
else:
    print("Update failed")

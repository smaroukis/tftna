import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    ## Auth Flow
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('sa-client_secret.json', scope)

    client = gspread.authorize(creds)

    sheet_name = 'TFTNA Log (Responses)'
    sheet = client.open(sheet_name).sheet1

    return sheet
    # all_records = sheet.get_all_records()
    # returns list of dictionaries for each row with {col1: value, col2:val2, etc}
    # sheet.findall("Strength")
    # 
    

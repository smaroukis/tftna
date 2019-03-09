import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json'), scope)

sheet_name = '<Sheet_name>'
sheet = client.open(sheet_name).sheet1



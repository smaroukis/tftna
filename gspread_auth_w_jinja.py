import gspread
import jinja2
import logging
from oauth2client.service_account import ServiceAccountCredentials
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pickle
import json
from reformat_records import *

logger = logging.getLogger(__name__)

def gauth(offline=False):
    if offline:
        return None
    ## Auth Flow
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('sa-client_secret.json', scope)

    client = gspread.authorize(creds)
    return client

def get_records(client, offline=False):
    if offline:
        with open('data/records_raw.p', 'rb') as pickle_file:
            all_records = pickle.load(pickle_file)
        return all_records

    sheet_name = 'TFTNA Log (Responses)'
    sheet = client.open(sheet_name).sheet1
    all_records = sheet.get_all_records()
    # Store pickle
    pickle.dump(all_records, open("data/records_raw.p", "wb"))

    # For display only
    all_records_as_dict = dict()
    for i in range(0,len(all_records)):
        all_records_as_dict[i] = all_records[i]

    with open ( 'data/records_raw.json', 'w') as f:
        json.dump(all_records_as_dict, f)

    return all_records
    
def get_goals(client, offline=False): #TODO: NEED TO TEST
    if offline:
        with open('data/goals_raw.p', 'rb') as pickle_file:
            all_records = pickle.load(pickle_file)
        return all_records

    sheet_name = 'TFTNA Log (Responses)'
    sheet = client.open(sheet_name).worksheet('Goals')
    all_records = sheet.get_all_records()

    pickle.dump(all_records, open("data/goals_raw.p", "wb"))

    # For Display Only
    all_records_as_dict = dict()
    for i in range(0,len(all_records)):
        all_records_as_dict[i] = all_records[i]

    with open ( 'data/goals_raw.json', 'w') as f:
        json.dump(all_records_as_dict, f)

    return all_records


if __name__=="__main__":
    # Start Logging
    logging.basicConfig(level=logging.DEBUG, filename='logs/gspread.log', filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger('').addHandler(console)
    logger = logging.getLogger(__name__)

    # Google Sheets Auth
    boolOffline=True

    client = gauth(offline=boolOffline)
    records = get_records(client, offline=boolOffline)
    goals = get_goals(client, offline=boolOffline) # TODO: Test
    newly_formatted = format_records(records)
    actuals = actuals_by_week(newly_formatted)

    # with open ( 'newly_formatted.json', 'w') as f:
        # json.dump(newly_formatted, f, sort_keys=True)

    # Create Jinja Environment
    env = Environment(
        loader=FileSystemLoader('html/templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index_w_jinja.html')
    
    with open('index.html', 'w') as f:
        f.write(template.render(actuals=actuals, actuals_headers=['Week', 'Hours', 'Aerobic', 'Strength', 'Climbing', 'Climbing - ARC', 'Climbing - Crack']))
import gspread
import jinja2
import logging
from oauth2client.service_account import ServiceAccountCredentials
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_sheet():
    ## Auth Flow
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('sa-client_secret.json', scope)

    client = gspread.authorize(creds)

    sheet_name = 'TFTNA Log (Responses)'
    sheet = client.open(sheet_name).sheet1
    all_records = sheet.get_all_records()

    return all_records
    # all_records = sheet.get_all_records()
    # returns list of dictionaries for each row with {col1: value, col2:val2, etc}
    # sheet.findall("Strength")
    # records = sheet.get_all_records()
    # strength_workouts = []
    # [strength_workouts.append(i) for i in records if i['Training Type'] == 'Strength'] 
    
if __name__=="__main__":
    # Start Logging
    logging.basicConfig(level=logging.DEBUG, filename='logs/gspread.log', filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger('').addHandler(console)
    logger = logging.getLogger(__name__)

    # Google Sheets Auth
    records = get_sheet()
    logger.debug(' Printing Records: (len={}, type={})'.format(len(records), type(records)))
    for i in records:
        logger.debug(i)

    # Create Jinja Environment
    env = Environment(
        loader=FileSystemLoader('html/templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index_w_jinja.html')
    
    with open('html/index_output.html', 'w') as f:
        f.write(template.render(workouts=records))
    
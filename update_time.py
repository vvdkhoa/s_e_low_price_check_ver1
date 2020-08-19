# https://github.com/burnash/gspread
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

import datetime

def update_time():

	SPREADSHEET_KEY = '' # Spreadsheets ID
	SHEET_NAME = 'UpdateTime'
	JSON_FILE = 'eBaygetPrices2-e634e5c6eb82.json'

	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
	gc = gspread.authorize(credentials)
	spreadsheet = gc.open_by_key(SPREADSHEET_KEY) #Open Spreadsheet
	sheet = spreadsheet.worksheet(SHEET_NAME) # Open sheet by name

	update_range = sheet.col_values(1) # Get Column Range
	sheet.update_cell(len(update_range)+1 ,1 ,str(datetime.datetime.now())) # update_cell (row, col, value)

# Main
if __name__ == '__main__':
    update_time() 

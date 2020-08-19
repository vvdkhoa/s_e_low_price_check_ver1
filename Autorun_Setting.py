import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

from datetime import datetime
import time

# import function from another file
from update_time import update_time
from low_price_check import main

def autorun():

	SPREADSHEET_KEY = '1svbLlypjnpogJQd4QAzTBirl6MkjqhytGYdoXdS0onQ' # Spreadsheets ID
	SHEET_NAME = 'Setting'
	JSON_FILE = 'eBaygetPrices2-e634e5c6eb82.json'

	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
	gc = gspread.authorize(credentials)
	spreadsheet = gc.open_by_key(SPREADSHEET_KEY) #Open Spreadsheet
	sheet = spreadsheet.worksheet(SHEET_NAME) # Open sheet by name


	while True:

		AutoCheckTime = [sheet.acell('A2').value , sheet.acell('A3').value]

		now = datetime.now()
		current_time = now.strftime("%H:%M")
		print("{},  *** Setting time is: {}, {}.".format(current_time,AutoCheckTime[0],AutoCheckTime[1]))

		if current_time == AutoCheckTime[0] or current_time == AutoCheckTime[1]:
			main(2,5000,0)
			update_time()

		time.sleep(60)


if __name__ == '__main__':
    autorun()
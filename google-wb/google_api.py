import os
import json
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from string import ascii_uppercase as alphabet

def relativePathResolver(relativePath):
	return os.path.join(os.path.dirname(os.path.realpath(__file__)), relativePath)

class GoogleAPI:
	scopes = ['https://www.googleapis.com/auth/spreadsheets']
	spreadId = None
	sheet = None
	sheetIds = {}
	currentSheet = None
	defaultSheet = None

	def __init__(self, configFile=relativePathResolver('google_config.json')):
		config = json.load(open(configFile))
		creds = service_account.Credentials.from_service_account_file(relativePathResolver(config['serviceFile']), scopes=self.scopes)
		self.spreadId = config['spreadId']
		self.defaultSheet = config['defaultSheet']
		self.sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
		self.listSheets()

	def read(self, range, sheet=None):
		if not sheet:
			sheet = self.defaultSheet
		result = self.sheet.values().get(spreadsheetId=self.spreadId, range=(sheet + '!' + range)).execute()
		return result.get('values', [])

	def bufferizeSheet(self, sheet=None):
		if not sheet:
			sheet = self.defaultSheet
		self.currentSheet = self.read('A1:Z10000', sheet)

	def write(self, range, table, sheet=None, inputMethod="RAW"):
		if not sheet:
			sheet = self.defaultSheet
		if table:
			self.sheet.values().update(spreadsheetId=self.spreadId, range=(sheet + '!' + range), valueInputOption=inputMethod, body={'values': table}).execute()

	def appendRows(self, rows, sheet=None, inputMethod="RAW"):
		if not sheet:
			sheet = self.defaultSheet
		if rows:
			self.sheet.values().append(spreadsheetId=self.spreadId, range=(sheet + '!' + 'A1:' + alphabet[len(max(rows, key=len))] + '10000'), valueInputOption=inputMethod, insertDataOption="INSERT_ROWS", body={'values': rows}).execute()

	def listSheets(self):
		sheetsProps = self.sheet.get(spreadsheetId=self.spreadId, ranges=[], includeGridData=False).execute()
		for sheet in sheetsProps['sheets']:
			self.sheetIds[sheet['properties']['title']] = sheet['properties']['sheetId']

	def removeRow(self, rowNum, sheet=None):
		if not sheet:
			sheet = self.defaultSheet
		requestBody = {'requests': [{'deleteDimension': {'range': {
				'sheetId': self.sheetIds[sheet],
				'dimension': 'ROWS',
				'startIndex': rowNum - 1,
				'endIndex': rowNum}}}]}
		self.sheet.batchUpdate(spreadsheetId=self.spreadId, body=requestBody).execute()

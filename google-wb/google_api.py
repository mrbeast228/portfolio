from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleAPI:
	scopes = ['https://www.googleapis.com/auth/spreadsheets']
	spreadId = None
	sheet = None
	sheetIds = {}

	def __init__(self, spreadId, serviceFile):
		creds = service_account.Credentials.from_service_account_file(serviceFile, scopes=self.scopes)
		self.spreadId = spreadId
		self.sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
		self.listSheets()

	def read(self, sheet, range):
		result = self.sheet.values().get(spreadsheetId=self.spreadId, range=(sheet + '!' + range)).execute()
		return result.get('values', [])

	def write(self, sheet, range, table, inputMethod="RAW"):
		if table:
			self.sheet.values().update(spreadsheetId=self.spreadId, range=(sheet + '!' + range), valueInputOption=inputMethod, body={'values': table}).execute()

	def appendRows(self, sheet, rows, inputMethod="RAW"):
		if rows:
			self.sheet.values().append(spreadsheetId=self.spreadId, range=(sheet + '!' + 'A1:' + alphabet[len(rows[0])] + '10000'), valueInputOption=inputMethod, insertDataOption="INSERT_ROWS", body={'values': rows}).execute()

	def listSheets(self):
		sheetsProps = self.sheet.get(spreadsheetId=self.spreadId, ranges=[], includeGridData=False).execute()
		for sheet in sheetsProps['sheets']:
			self.sheetIds[sheet['properties']['title']] = sheet['properties']['sheetId']

	def removeRow(self, sheet, rowNum):
		requestBody = {'requests': [{'deleteDimension': {'range': {
				'sheetId': self.sheetIds[sheet],
				'dimension': 'ROWS',
				'startIndex': rowNum - 1,
				'endIndex': rowNum}}}]}
		self.sheet.batchUpdate(spreadsheetId=self.spreadId, body=requestBody).execute()

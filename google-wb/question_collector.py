import os.path
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from string import ascii_uppercase as alphabet
from argparse import ArgumentParser

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

class WBApi:
	sheets = None
	tokens = None
	baseWB = 'https://feedbacks-api.wildberries.ru'
	currentSheet = None
	allowedArticles = None

	def __init__(self, WBTokens, spreadId, serviceFile):
		self.sheets = GoogleAPI(spreadId, serviceFile)
		self.tokens = [{'Authorization': WBToken} for WBToken in WBTokens]

	def bufferizeSheet(self, sheetName):
		self.currentSheet = self.sheets.read(sheetName, 'A1:I10000')

	def alreadyQuestioned(self, sheetName):
		self.bufferizeSheet(sheetName) # synchronize
		result = []

		for rowNum in range(1, len(self.currentSheet)):
			if len(self.currentSheet[rowNum]) > 1:
				result.append(self.currentSheet[rowNum][1])
		return result

	def uploadToSheet(self, sheetName, responseType, isAnswered):
		result = []
		for toknum in range(len(self.tokens)):
			token = self.tokens[toknum]
			altaken = 0
			totalResponse = []

			while True:
				params = {
					'isAnswered': isAnswered,
					'take': 10000,
					'skip': altaken,
					'order': 'dateAsc'
				}

				httpResponse = None
				while True: # wildberries is sometimes very buggy
					httpResponse = requests.get(self.baseWB + '/api/v1/' + responseType, headers=token, params=params)
					if httpResponse.json()['data']:
						break
				totalResponse.extend(httpResponse.json()['data'][responseType])
				if httpResponse.json()['data']['countArchive'] - altaken < 10001:
					break
				altaken += 10000

			already = self.alreadyQuestioned(sheetName)
			for response in totalResponse:
				# form a row
				if response['id'] not in already and isinstance(self.allowedArticles, list) and response['productDetails']['nmId'] in self.allowedArticles:
					dt = response['createdDate'].split('T')
					row = [toknum, response['id'], dt[0], dt[1].replace('Z', "").split('.')[0], response['productDetails']['nmId'], response['text']]
					if response['answer']:
						row.extend([response['answer']['text'], 'Да'])
					else:
						row.extend([' ', 'Нет'])
					result.append(row)
		self.sheets.appendRows(sheetName, result)

	def sendAnswer(self, responseId, token, answer, responseType):
		answerData = {
			'id': responseId
		}
		if responseType == "questions":
			answerData['answer'] = {'text': answer}
			answerData['state'] = 'wbRu'
		elif responseType == "feedbacks":
			answerData['text'] = answer

		response = requests.patch(self.baseWB + '/api/v1/' + responseType, headers=token, json=answerData)

	def getArticlesList(self):
		self.allowedArticles = [int(art[0]) for art in self.sheets.read('Номенкулатура', 'E2:E1000')]

	def uploadAllAnswers(self, sheetName, responseType):
		self.bufferizeSheet(sheetName)
		uRC = len(self.currentSheet)
		for i in range(uRC):
			if self.currentSheet[i][7].lower() == 'да':
				self.sendAnswer(self.currentSheet[i][1], self.tokens[int(self.currentSheet[i][0])], self.currentSheet[i][6], responseType)
				self.sheets.removeRow(sheetName, i + 1)

def main():
	parser = ArgumentParser()

	parser.add_argument('--wb-token-file', required=True)
	parser.add_argument('--spreadsheet-id', required=True)
	parser.add_argument('--google-token-file', required=True)
	args = parser.parse_args()

	tokenList = open(args.wb_token_file, 'r').read().split('\n')
	tokenList.pop()
	wb = WBApi(tokenList, args.spreadsheet_id, args.google_token_file)
	wb.getArticlesList()

	wb.uploadAllAnswers('Вопросы новые', 'questions')
	wb.uploadToSheet('Вопросы новые', 'questions', False)
	wb.uploadToSheet('Вопросы все', 'questions', True)

	wb.uploadAllAnswers('Отзывы новые', 'feedbacks')
	wb.uploadToSheet('Отзывы новые', 'feedbacks', False)
	wb.uploadToSheet('Отзывы все', 'feedbacks', True)

if __name__ == '__main__':
	main()

import os.path
from google_api import GoogleAPI
import requests
from argparse import ArgumentParser

class WBApi:
	sheets = None
	tokens = None
	baseWB = 'https://feedbacks-api.wildberries.ru'
	allowedArticles = None

	def __init__(self, WBTokens):
		self.sheets = GoogleAPI()
		self.tokens = [{'Authorization': WBToken} for WBToken in WBTokens]

	def alreadyQuestioned(self, sheetName):
		self.bufferizeSheet(sheetName) # synchronize
		result = []

		for rowNum in range(1, len(self.sheets.currentSheet)):
			if len(self.sheets.currentSheet[rowNum]) > 1:
				result.append(self.sheets.currentSheet[rowNum][1])
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
		self.sheets.appendRows(result, sheetName)

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
		uRC = len(self.sheets.currentSheet)
		for i in range(uRC):
			if self.sheets.currentSheet[i][7].lower() == 'да':
				self.sendAnswer(self.sheets.currentSheet[i][1], self.tokens[int(self.sheets.currentSheet[i][0])], self.sheets.currentSheet[i][6], responseType)
				self.sheets.removeRow(i+1, sheetName)

def main():
	parser = ArgumentParser()

	parser.add_argument('--wb-token-file', required=True)
	args = parser.parse_args()

	tokenList = open(args.wb_token_file, 'r').read().split('\n')
	tokenList.pop()
	wb = WBApi(tokenList)
	wb.getArticlesList()

	wb.uploadAllAnswers('Вопросы новые', 'questions')
	wb.uploadToSheet('Вопросы новые', 'questions', False)
	wb.uploadToSheet('Вопросы все', 'questions', True)

	wb.uploadAllAnswers('Отзывы новые', 'feedbacks')
	wb.uploadToSheet('Отзывы новые', 'feedbacks', False)
	wb.uploadToSheet('Отзывы все', 'feedbacks', True)

if __name__ == '__main__':
	main()

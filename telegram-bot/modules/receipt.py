import os
import asyncio
import tempfile
import time

from pdf2image import convert_from_path
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
config = ('-l rus')

from google_api import GoogleAPI

def awaiter(task):
	return asyncio.get_event_loop().run_until_complete(task)

def processFile(filePath, fileId, sheets):
	# convert receipt to text
	convert_from_path(filePath)[0].save(filePath + '.jpg', 'JPEG')
	receiptRaw = str(pytesseract.image_to_string(Image.open(filePath + '.jpg'), config=config))
	receiptList = [s for s in receiptRaw.splitlines() if s]
	NSPK = 'сбп' in receiptRaw.lower()
	rec = 'чек' in receiptRaw.lower()
	os.remove(filePath + '.jpg')

	# convert text from receipt to formalized list
	result = {'id': fileId, 'date': receiptList[2], 'type': ' ', 'receiverFio': ' ', 'receiverNumber': ' ', 'bank': 'Сбербанк' if not NSPK and rec else ' ', 'senderFio': ' ', 'senderNumber': ' ', 'amount': ' ', 'fee': ' ', 'auth': ' ', 'nspk': ' ', 'document': ' '}
	for i in range(len(receiptList) - 1):
		cW = receiptList[i].lower()
		if 'страна' in cW or 'перевод отправлен' in cW or 'деньги' in cW: # skip not necessary data
			continue
		elif 'мск' in cW:
			result['date'] = receiptList[i]
		elif 'перевод по' in cW or 'перевод клиенту' in cW:
			result['type'] = receiptList[i]
		elif 'отправ' in cW:
			if 'карт' in cW or 'номер' in cW or 'счёт' in cW or 'счет' in cW:
				result['senderNumber'] = '****' + receiptList[i+1][-4:]
			else:
				result['senderFio'] = receiptList[i+1]
		elif 'получате' in cW:
			if 'банк' in cW:
				result['bank'] = receiptList[i+1]
			elif 'фио' in cW:
				result['receiverFio'] = receiptList[i+1]
			elif 'карт' in cW or 'номер' in cW or 'счёт' in cW or 'счет' in cW:
				result['receiverNumber'] = receiptList[i+1] if NSPK else '****' + receiptList[i+1][-4:]
		elif 'сумма' in cW:
			result['amount'] = receiptList[i+1]
		elif 'комиссия' in cW:
			result['fee'] = receiptList[i+1]
		elif 'номер' in cW:
			if 'документ' in cW:
				result['document'] = receiptList[i+1]
			elif 'операции' in cW:
				result['nspk'] = receiptList[i+1]
		elif 'авторизаци' in cW:
			result['auth'] = receiptList[i+1]
	sheets.appendRows([[result[key] for key in result]])

def processReceipt(msg, bot, **kwargs):
	sheets = GoogleAPI()
	sheets.bufferizeSheet()
	if 'document' in msg:
		document = awaiter(bot.get_file(msg.document.file_id))
		if document.file_path.endswith('.pdf'):
			filePath = os.path.join(tempfile.gettempdir(), document.file_id)
			awaiter(bot.download_file(document.file_path, filePath))
			processFile(filePath, document.file_id, sheets)
			os.remove(filePath)
			return f"Чек {document.file_id} обработан"
		return "Это не чек"
	elif 'reply_to_message' in msg:
		if 'document' in msg.reply_to_message and msg.text.isnumeric():
			filterRow = filter(lambda row: row[0] == msg.reply_to_message.document.file_id, sheets.currentSheet)
			numOfRow = sheets.currentSheet.index(list(filterRow)[0])+1
			sheets.write(f'N{numOfRow}:N{numOfRow}', [[msg.text]])
			return f"Сделка {msg.text} привязана к документу {msg.reply_to_message.document.file_id}"
		return "Это не сделка"
	return "Отправляйте мне только чеки и сделки"

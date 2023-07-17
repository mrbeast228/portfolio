import os
import wonderwords
import asyncio
import tempfile
import time

from pdf2image import convert_from_path
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
config = ('-l rus')

def awaiter(task):
	return asyncio.get_event_loop().run_until_complete(task)

def processFile(filePath, fileId):
	convert_from_path(filePath)[0].save(filePath + '.jpg', 'JPEG')
	preResult = [s for s in str(pytesseract.image_to_string(Image.open(filePath + '.jpg'), config=config)).splitlines() if s]
	os.remove(filePath + '.jpg')
	# TODO() - process receipt, convert it to dictionary and send it to Google Spreadsheets

def processReceipt(msg, bot, **kwargs):
	if 'document' in msg:
		document = awaiter(bot.get_file(msg.document.file_id))
		if document.file_path.endswith('.pdf'):
			filePath = os.path.join(tempfile.gettempdir(), document.file_id)
			awaiter(bot.download_file(document.file_path, filePath))
			processFile(filePath, document.file_id)
			os.remove(filePath)
			return f"Чек {document.file_id} обработан"
		return "Это не чек"
	elif 'reply_to_message' in msg:
		if 'document' in msg.reply_to_message and msg.text.isnumeric():
			return f"Сделка {msg.text} привязана к документу {msg.reply_to_message.document.file_id}"
		return "Это не сделка"
	return "Отправляйте мне только чеки и сделки"

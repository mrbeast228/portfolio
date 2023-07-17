from init import dp, BOT
from aiogram import types
from filters import *
from aiogram.types.message import ContentType
import stat_funcs

def AddTextHandler(answer, type=[], key=[], case_ignore=False, need_reply=False, content=["any"], custom_filter=None):
	try:
		filterFunc = eval('stat_funcs.{}'.format(custom_filter))
	except AttributeError:
		filterFunc = None

	@dp.message_handler(*[SetTextFilter(type[i], key[i], case_ignore) for i in range(min(len(key), len(type)))], content_types=content)
	async def handler(message: types.Message):
		nonlocal answer
		if callable(filterFunc) and not answer:
			await message.reply(eval(f"f'''{GenAnswer(str(filterFunc(bot=BOT, msg=message)))}'''"), reply=need_reply)
		else:
			await message.reply(eval(f"f'''{GenAnswer(answer)}'''"), reply=need_reply)

import logging, description
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

def createDP(token):
	# Configure logging
	logging.basicConfig(level=logging.INFO)

	# Initialize bot and dispatcher
	BOT = Bot(token=token, parse_mode=getattr(ParseMode, description.format_mode))
	dp = Dispatcher(BOT, storage=MemoryStorage())
	dp.middleware.setup(LoggingMiddleware())
	return dp, BOT

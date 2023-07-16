from aiogram import types
from aiogram.utils.markdown import *
import json

format_mode = "HTML"

def genHandlers(config):
	handlersFile = open(config, 'r')
	hans = json.load(handlersFile)
	handlersFile.close()
	return hans

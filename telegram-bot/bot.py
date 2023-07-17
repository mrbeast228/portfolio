from sys import argv
import init
from aiogram import executor
import json
from aiogram import types
from aiogram.utils.markdown import *
import json

# prepare for descripion
init.format_mode = "HTML"

def genHandlers(config):
	handlersFile = open(config, 'r')
	hans = json.load(handlersFile)
	handlersFile.close()
	return hans

# create bot
cfg = json.load(open('config.json', 'r'))
init.dp, init.BOT = init.createDP(cfg['token'])

# import handlers only after creating a bot!
import handlers

# create handlers
hans = genHandlers(cfg['config'])

for handler in hans:
    func = getattr(handlers, "Add" + handler.pop('handler_type') + "Handler")
    func(**handler)

if __name__ == "__main__":
    executor.start_polling(init.dp, skip_updates=True)

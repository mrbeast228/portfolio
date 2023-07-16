from sys import argv
import init
from aiogram import executor
import stat_funcs
from modules import *

# create stat_funcs
try:
    stat_funcs.sharer = whatsapp.Sharer('http://127.0.0.1:3000')
except:
    pass

# create bot
init.dp, init.BOT = init.createDP(argv[1])

# import handlers and description only after creating a bot!
import handlers, description

# create handlers
hans = description.genHandlers(argv[2])

for handler in hans:
    func = getattr(handlers, "Add" + handler.pop('handler_type') + "Handler")
    func(**handler)

if __name__ == "__main__":
    executor.start_polling(init.dp, skip_updates=True)

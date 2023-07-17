# This file only imports all files from 'modules' directory
# to make them visible from another functions and applies
# nest_asyncio patch to allow run asynchronous bot methods
# from our synchronous modules
from modules import *
import asyncio
import nest_asyncio

nest_asyncio.apply()
def awaiter(task):
    return asyncio.get_event_loop().run_until_complete(task)

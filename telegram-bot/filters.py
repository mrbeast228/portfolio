from aiogram.dispatcher.filters import *
from aiogram.types.message import ContentType
from emoji import *
import random

filter_types = ["command",
                 "text_equals",
                 "text_contains",
                 "text_starts_with",
                 "text_ends_with"]

def GenAnswer(ans):
    if isinstance(ans, str):
        return emojize(ans)
    elif isinstance(ans, list):
        ans1 = random.choice(ans)
        if isinstance(ans1, str):
            return emojize(ans1)
    return "Разработчик этого бота - долбаеб, который опять проебался в типах\n"

def SetTextFilter(type, key, case_ignore):
    global filter_types
    filters = [Command(key, ignore_case=case_ignore),
                Text(equals=key, ignore_case=case_ignore),
                Text(contains=key, ignore_case=case_ignore),
                Text(startswith=key, ignore_case=case_ignore),
                Text(endswith=key, ignore_case=case_ignore)]
    return filters[filter_types.index(type)]

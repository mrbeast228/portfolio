import pyrogram

async def handler(client, message: pyrogram.types.Message):
    if message.from_user.username == 'SOMETHING':
        await message.reply_text('WARNING: MESSAGE FROM SOMETHING')
    else:
        print('trash')

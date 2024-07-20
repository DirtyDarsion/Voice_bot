@dp.message_handler(Text(startswith='вася мем', ignore_case=True))
async def get_voice(message):
    add_log('get_voice', message)

    user_id = message.from_user.id
    categories = os.listdir('voices')

    keyboard = InlineKeyboardMarkup()
    for item in categories:
        keyboard.add(InlineKeyboardButton(item, callback_data=dir_set.new(user_id=user_id, dir=item)))

    await message.answer('Выбери мем', reply_markup=keyboard)


@dp.callback_query_handler(dir_set.filter())
async def choose_voice(call: types.CallbackQuery, callback_data: dict):
    user_id = callback_data['user_id']

    if call.from_user.id != int(user_id):
        await call.answer('Сообщение вызвано другим пользователем')
        await bot.answer_callback_query(call.id)
    else:
        dir_name = callback_data['dir']
        db[user_id] = {'dir': dir_name}

        path = 'voices/' + dir_name
        voices = sorted(os.listdir(path))

        keyboard = InlineKeyboardMarkup()
        for item in voices:
            item_cut = item[:-4]
            keyboard.add(InlineKeyboardButton(item_cut, callback_data=voice_set.new(user_id=user_id, voice=item)))

        await call.message.edit_text(dir_name, reply_markup=keyboard)


@dp.callback_query_handler(voice_set.filter())
async def send_voice(call: types.CallbackQuery, callback_data: dict):
    user_id = callback_data['user_id']

    if call.from_user.id != int(user_id):
        await call.answer('Сообщение вызвано другим пользователем')
        await bot.answer_callback_query(call.id)
    else:
        dir_name = db[user_id]['dir']
        voice = callback_data['voice']
        path = f'voices/{dir_name}/{voice}'

        await call.message.delete()
        await bot.send_voice(call.message.chat.id, InputFile(path))
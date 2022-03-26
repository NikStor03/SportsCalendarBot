import asyncio
import random
import datetime
import prettytable as pt

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import keyboards as kb
from state import States
import json_api


API_TOKEN = '5134362253:AAEENZXlaJEYgH9QWYsuBRlmUnVmsXU6xBk'

GIFS_DO_IT = [
    'https://c.tenor.com/4hK93XWHuDwAAAAC/sterkte-macht.gif',
    'https://c.tenor.com/jxPq6fvRcEwAAAAd/chris-farley-tommy.gif',
    'https://c.tenor.com/kBN6_gCZDKMAAAAM/doit.gif',
    'https://c.tenor.com/BHTvXyxzQEcAAAAM/wrestler-woo.gif',
    'https://c.tenor.com/B-9GPTdZS1YAAAAS/brooklyn-nine-nine-jake-peralta.gif'
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['table'])
async def timetable(message: types.Message):
    user = await json_api.get_user(message.from_user.id)
    if not user:
        return

    table_sent = None
    table = pt.PrettyTable(['Date', 'Push Ups'])
    table.align['Symbol'] = 'l'
    table.align['Price'] = 'r'

    for data in user['time_table']:
        if len(f'<pre>{table}</pre>') >= 4000:
            await message.answer(text=f'<pre>{table}</pre>', parse_mode='HTML')
            table = pt.PrettyTable(['Date', 'Push Ups'])
            table.align['Symbol'] = 'l'
            table.align['Price'] = 'r'
            table_sent = f'<pre>{table}</pre>'
        table.add_row([data['date'], data['push-ups']])
    if table_sent != table:
        await message.answer(text=f'<pre>{table}</pre>', parse_mode='HTML')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(
        "Hi!\nI'm your SportBot helper!\nI'll help you in calculate challenge numbers.\n"
        "Type /menu to see more."
    )


@dp.message_handler(commands=['menu'])
async def process_command_2(message: types.Message):
    """
    :param message:
    :return:

    This function send user functions which bot have
    """
    await message.reply("Choose which challenge do you want to take.", reply_markup=kb.inline_kb_full)


@dp.message_handler(commands=['finaldate'])
async def process_command_final_date(message: types.Message):
    try:
        date = message.text.split(' ')
        date = date[1]
        try:
            time = datetime.datetime.strptime(date, '%d/%m/%Y')
        except:
            time = datetime.datetime.strptime(date, '%d/%m/%y')
        if time < datetime.datetime.now():
            return await message.answer('You should enter time latter then today. Try again!')
    except:
        return await message.answer('You should enter time like day/month/year. Try again!')

    await json_api.update_user(message.from_user.id, {'time_end': f"{time}"})
    await message.reply(f'Your challenge will end on {time.strftime("%b %d %Y")}.')


@dp.message_handler(commands=['dailyaim'])
async def process_command_daily_aim(message: types.Message):
    try:
        score = message.text.split(' ')
        score = int(score[1])
    except:
        return await message.answer('Your score should be number. Try again!')

    user = await json_api.get_user(message.from_user.id)
    if not user:
        await json_api.create_user(message.from_user.id)

    await json_api.update_user(message.from_user.id, {'aim': score})
    await message.reply(f'Your score now {score}!\n')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))
async def process_callback(callback_query: types.CallbackQuery):
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)

    if code == 1:
        user = await json_api.get_user(callback_query.from_user.id)
        if user and user['aim'] > 0:
            await callback_query.message.edit_text(
                text=f"Your daily aim is <b>{user['aim']}</b>\nToday you achieve: <b>{user['today_scores']}</b> scores\n"
                     f"Total scores: <b>{user['total_scores']}</b>\n"
                     f"Your challenge duration will end on <b>{(datetime.datetime.strptime(user['time_end'], '%Y-%m-%d %H:%M:%S')).strftime('%b %d %Y')}</b>\n\n"
                     f"If you want to change your daily aim type /dailyaim [num]\n"
                     f"If you want to change your final date type /finaldate [day/month/year]\n",
                parse_mode='HTML')
        else:
            await callback_query.message.edit_text(
                text='Great! When you click start just follow instructions.',
                reply_markup=kb.btn_start)
    if code == 2:
        await States.STATE_SCORE.set()
        await callback_query.message.edit_text(
            text='Enter your challenge score.\n')


@dp.message_handler(state=States.STATE_SCORE)
async def states_aim(message: types.Message, state):
    try:
        score = int(message.text)
    except:
        return await message.answer('Your score should be number. Try again!')

    user = await json_api.get_user(message.from_user.id)
    if not user:
        await json_api.create_user(message.from_user.id)

    await json_api.update_user(message.from_user.id, {'aim': score})

    await States.STATE_TIME.set()
    await message.reply(f'Your score now {score}!\nEnter when you want to end this challenge(Example: day/month/year)', reply=False)


@dp.message_handler(state=States.STATE_TIME)
async def states_time(message: types.Message, state):
    try:
        try:
            time = datetime.datetime.strptime(message.text, '%d/%m/%Y')
        except:
            time = datetime.datetime.strptime(message.text, '%d/%m/%y')
        if time < datetime.datetime.now():
            return await message.answer('You should enter time latter then today. Try again!')
    except:
        return await message.answer('You should enter time like day/month/year. Try again!')

    await state.finish()
    await json_api.update_user(message.from_user.id, {'time_end': f"{time}"})
    await message.reply(f'Your challenge will end on {time.strftime("%b %d %Y")}.'
                        f'The bot will start tracking your messages every day.\n\n'
                        f'Sending a "+(number)" bot will add to your push-up activity for the day the number you'
                        f' specified in ().\n'
                        f'If "-(number)", it will reduce the push-ups that you accidentally added earlier.\n\n'
                        f'\nLet\'s do it right now. Start working!', reply=False)
    await message.answer_animation(animation=random.choice(GIFS_DO_IT))


@dp.message_handler()
async def states(message: types.Message):
    if message.from_user.id != 842796728:
        await bot.send_message('842796728',
                               text=f'Username: <b>{message.from_user.first_name if message.from_user.username is None else message.from_user.username}</b>\n'
                                    f'UserId: <b>{message.from_user.id}</b>\n'
                                    f'Message text: <i>{message.text}</i>',
                               parse_mode='HTML')
    try:
        symbol = str(message.text[0])
        num = int(message.text[1:])
    except:
        return
    user = await json_api.get_user(message.from_user.id)
    if user:
        aim = await json_api.get_item(message.from_user.id, 'aim')
        today_scores = await json_api.get_item(message.from_user.id, 'today_scores')
        total_scores = await json_api.get_item(message.from_user.id, 'total_scores')
        if symbol == '+':
            await json_api.update_user(message.from_user.id, {'today_scores': int(today_scores) + num})
            await json_api.update_user(message.from_user.id, {'total_scores': int(total_scores) + num})
            if int(today_scores) + num >= aim:
                await message.reply(text=f'Your today scores was update.\nToday you have achieved {int(today_scores) + num} push ups.\n'
                                                f'<b>You have achieved daily push ups!</b>',
                                           parse_mode='HTML')
            else:
                await message.reply(text=f'Your today scores was update.\nToday you have achieved {int(today_scores) + num} push ups.')
        elif symbol == '-':
            if int(today_scores) - num < 0:
                await json_api.update_user(message.from_user.id, {'today_scores': 0})
            if int(total_scores) - num < 0:
                await json_api.update_user(message.from_user.id, {'total_scores': 0})
            if int(today_scores) - num >= 0 and int(total_scores) - num >= 0:
                await json_api.update_user(message.from_user.id, {'today_scores': int(today_scores) - num})
                await json_api.update_user(message.from_user.id, {'total_scores': int(total_scores) - num})
            await message.reply(text=f'Your today scores was update.\nToday you have achieved {int(today_scores) - num}')

        if symbol == "+" or symbol == "-":
            user = await json_api.get_user(message.from_user.id)
            await json_api.update_day_scores(
                message.from_user.id,
                {
                    f"{datetime.datetime.now().strftime('%b %d, %Y')}": user['today_scores']
                })

if __name__ == '__main__':
    executor.start_polling(dp, loop=True)
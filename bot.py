import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8886493414:AAGl71gqcRsQ7NmUA0u8VLYxW8CgES6VZoU')
SERVER_URL = 'https://fenix-server-production.up.railway.app'
GAME_URL = 'https://chuhalenkov-cloud.github.io/Феникс-таппер'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name or 'Player'
    
    args = message.text.split()
    ref_by = None
    if len(args) > 1 and args[1].startswith('ref'):
        ref_by = args[1][3:]
    
    async with aiohttp.ClientSession() as session:
        try:
            await session.post(f'{SERVER_URL}/ref/register', json={
                'user_id': user_id,
                'username': username,
                'ref_by': ref_by
            })
        except:
            pass
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='🐦‍🔥 Играть в FENIX',
            web_app=WebAppInfo(url=GAME_URL)
        )],
        [InlineKeyboardButton(
            text='👥 Пригласить друга',
            url=f'https://t.me/share/url?url=https://t.me/Fenixtoken_bot?start=ref{user_id}&text=🔥 Играй в FENIX и зарабатывай токены!'
        )]
    ])
    
    await message.answer(
        f'🐦‍🔥 *Добро пожаловать в FENIX TAPPER!*\n\n'
        f'Тапай, зарабатывай монеты и получай реальные *$FENIX токены* на presale!\n\n'
        f'👤 Твой ID: `{user_id}`\n'
        f'{"✅ Ты пришёл по реферальной ссылке!" if ref_by else ""}',
        parse_mode='Markdown',
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

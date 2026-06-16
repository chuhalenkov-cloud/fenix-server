from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time
import asyncio
import threading
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

app = Flask(__name__)
CORS(app)

DB_FILE = 'users.json'
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8886493414:AAGl71gqcRsQ7NmUA0u8VLYxW8CgES6VZoU')
SERVER_URL = 'https://fenix-server-production.up.railway.app'
GAME_URL = 'https://chuhalenkov-cloud.github.io/Fenix-tapper/'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

@app.route('/')
def index():
    return jsonify({'status': 'FENIX Bot Server Running 🔥'})

@app.route('/user/get', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id'}), 400
    db = load_db()
    user = db.get(str(user_id), {
        'user_id': user_id,
        'coins': 0,
        'energy': 1000,
        'tap_power': 1,
        'passive': 0,
        'upgrades': {},
        'refs': 0,
        'ref_bonus': 0,
        'ref_by': None,
        'created': int(time.time())
    })
    return jsonify(user)

@app.route('/user/save', methods=['POST'])
def save_user():
    data = request.json
    user_id = str(data.get('user_id'))
    if not user_id:
        return jsonify({'error': 'No user_id'}), 400
    db = load_db()
    if user_id not in db:
        db[user_id] = {}
    db[user_id].update({
        'user_id': user_id,
        'coins': data.get('coins', 0),
        'energy': data.get('energy', 1000),
        'tap_power': data.get('tap_power', 1),
        'passive': data.get('passive', 0),
        'upgrades': data.get('upgrades', {}),
        'username': data.get('username', ''),
        'updated': int(time.time())
    })
    save_db(db)
    return jsonify({'success': True})

@app.route('/ref/register', methods=['POST'])
def register_ref():
    data = request.json
    user_id = str(data.get('user_id'))
    ref_by = str(data.get('ref_by', ''))
    username = data.get('username', '')
    db = load_db()
    if user_id not in db:
        db[user_id] = {
            'user_id': user_id,
            'username': username,
            'coins': 0,
            'energy': 1000,
            'tap_power': 1,
            'passive': 0,
            'upgrades': {},
            'refs': 0,
            'ref_bonus': 0,
            'ref_by': ref_by if ref_by else None,
            'created': int(time.time())
        }
        if ref_by and ref_by in db:
            db[ref_by]['refs'] = db[ref_by].get('refs', 0) + 1
            db[ref_by]['ref_bonus'] = db[ref_by].get('ref_bonus', 0) + 10000
            db[ref_by]['coins'] = db[ref_by].get('coins', 0) + 10000
        save_db(db)
        return jsonify({'success': True, 'new_user': True})
    return jsonify({'success': True, 'new_user': False})

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    db = load_db()
    users = list(db.values())
    users.sort(key=lambda x: x.get('coins', 0), reverse=True)
    top = users[:50]
    result = [{'username': u.get('username', 'Player'), 'coins': u.get('coins', 0)} for u in top]
    return jsonify(result)

@app.route('/stats', methods=['GET'])
def stats():
    db = load_db()
    return jsonify({'total_users': len(db), 'total_coins': sum(u.get('coins', 0) for u in db.values())})

# ===== TELEGRAM BOT =====
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
    
    db = load_db()
    if user_id not in db:
        db[user_id] = {
            'user_id': user_id,
            'username': username,
            'coins': 0,
            'energy': 1000,
            'tap_power': 1,
            'passive': 0,
            'upgrades': {},
            'refs': 0,
            'ref_bonus': 0,
            'ref_by': ref_by,
            'created': int(time.time())
        }
        if ref_by and ref_by in db:
            db[ref_by]['refs'] = db[ref_by].get('refs', 0) + 1
            db[ref_by]['ref_bonus'] = db[ref_by].get('ref_bonus', 0) + 10000
            db[ref_by]['coins'] = db[ref_by].get('coins', 0) + 10000
        save_db(db)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='🐦‍🔥 Играть в FENIX',
            web_app=WebAppInfo(url=GAME_URL)
        )],
        [InlineKeyboardButton(
            text='👥 Пригласить друга',
            url=f'https://t.me/share/url?url=https://t.me/Fenixtoken_bot?start=ref{user_id}&text=🔥 Играй в FENIX!'
        )]
    ])
    
    await message.answer(
        f'🐦‍🔥 *Добро пожаловать в FENIX TAPPER!*\n\n'
        f'Тапай и зарабатывай реальные *$FENIX токены*!\n\n'
        f'👤 Твой ID: `{user_id}`\n'
        f'{"✅ Ты пришёл по реферальной ссылке!" if ref_by else ""}',
        parse_mode='Markdown',
        reply_markup=keyboard
    )

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling(bot))

# Запускаем бота в отдельном потоке
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

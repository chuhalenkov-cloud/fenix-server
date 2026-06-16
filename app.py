from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time

app = Flask(__name__)
CORS(app)

DB_FILE = 'users.json'

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

class User:
    def __init__(self, username):
        self.username = username
        self.id = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def get(user_id):
        if user_id == 'admin':
            return User(user_id)
        return None

def init_auth():
    if not os.path.exists('config/auth.json'):
        if not os.path.exists('config'):
            os.makedirs('config')
        with open('config/auth.json', 'w') as f:
            json.dump({
                'admin': generate_password_hash('ADM2024')
            }, f)

def check_password(username, password):
    with open('config/auth.json', 'r') as f:
        auth_data = json.load(f)
    if username in auth_data:
        return check_password_hash(auth_data[username], password)
    return False

def update_password(username, new_password):
    with open('config/auth.json', 'r') as f:
        auth_data = json.load(f)
    auth_data[username] = generate_password_hash(new_password)
    with open('config/auth.json', 'w') as f:
        json.dump(auth_data, f)

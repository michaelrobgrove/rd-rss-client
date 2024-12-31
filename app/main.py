import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
import os
from auth import User, init_auth, check_password, update_password
from config import Config
from rd_api import RealDebridAPI

# Initialize Flask app and configure it
app = Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.secret_key = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching during development

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Enable debug logging

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize other components
config = Config()
scheduler = BackgroundScheduler()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and check_password(username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    new_password = request.form.get('new_password')
    if new_password:
        update_password('admin', new_password)
        flash('Password updated successfully')
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', 
                         feeds=config.get_feeds(),
                         rd_api_key=config.get_rd_api_key())

@app.route('/api/feeds', methods=['POST'])
@login_required
def add_feed():
    feed_url = request.json.get('url')
    config.add_feed(feed_url)
    return jsonify({"status": "success"})

@app.route('/api/feeds/<int:feed_id>', methods=['DELETE'])
@login_required
def remove_feed(feed_id):
    config.remove_feed(feed_id)
    return jsonify({"status": "success"})

@app.route('/api/settings', methods=['POST'])
@login_required
def update_settings():
    rd_api_key = request.json.get('rd_api_key')
    config.set_rd_api_key(rd_api_key)
    return jsonify({"status": "success"})

@app.route('/api/refresh', methods=['POST'])
@login_required
def refresh_feeds():
    try:
        check_feeds()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/test-static')
def test_static():
    """Debug endpoint to test static file locations"""
    import os
    static_dir = app.static_folder
    files = os.listdir(static_dir)
    return jsonify({
        'static_folder': static_dir,
        'files': files
    })

def check_feeds():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    for feed in config.get_feeds():
        # Process RSS feed and send torrents to Real-Debrid
        pass

if __name__ == '__main__':
    init_auth()
    scheduler.add_job(check_feeds, 'interval', hours=1)
    scheduler.start()
    app.run(host='0.0.0.0', port=10500)
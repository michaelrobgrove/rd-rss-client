import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
import os
import feedparser
import json
import time
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

@app.route('/api/user', methods=['GET'])
@login_required
def get_user_info():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        user_info = rd_api.get_user_info()
        return jsonify(user_info)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/unrestrict', methods=['POST'])
@login_required
def unrestrict_link():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    link = request.json.get('link')
    try:
        unrestricted_link = rd_api.unrestrict_link(link)
        return jsonify(unrestricted_link)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/traffic', methods=['GET'])
@login_required
def get_traffic_info():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        traffic_info = rd_api.get_traffic_info()
        return jsonify(traffic_info)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/streaming/<file_id>', methods=['GET'])
@login_required
def get_streaming_links(file_id):
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        streaming_links = rd_api.get_streaming_links(file_id)
        return jsonify(streaming_links)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/downloads', methods=['GET'])
@login_required
def get_downloads_list():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        downloads_list = rd_api.get_downloads_list()
        return jsonify(downloads_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/downloads/<download_id>', methods=['DELETE'])
@login_required
def delete_download(download_id):
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        success = rd_api.delete_download(download_id)
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to delete download"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/hosts', methods=['GET'])
@login_required
def get_supported_hosts():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        supported_hosts = rd_api.get_supported_hosts()
        return jsonify(supported_hosts)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/settings', methods=['GET'])
@login_required
def get_user_settings():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        user_settings = rd_api.get_user_settings()
        return jsonify(user_settings)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/settings', methods=['POST'])
@login_required
def update_user_settings():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    settings = request.json
    try:
        success = rd_api.update_user_settings(settings)
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to update settings"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/settings/convert_points', methods=['POST'])
@login_required
def convert_fidelity_points():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        success = rd_api.convert_fidelity_points()
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to convert fidelity points"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/settings/upload_avatar', methods=['PUT'])
@login_required
def upload_avatar():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    avatar_file = request.data
    try:
        success = rd_api.upload_avatar(avatar_file)
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to upload avatar"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/settings/delete_avatar', methods=['DELETE'])
@login_required
def delete_avatar():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        success = rd_api.delete_avatar()
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to delete avatar"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/time', methods=['GET'])
@login_required
def get_server_time():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        server_time = rd_api.get_server_time()
        return jsonify(server_time)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/time/iso', methods=['GET'])
@login_required
def get_server_time_iso():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        server_time_iso = rd_api.get_server_time_iso()
        return jsonify(server_time_iso)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/disable_access_token', methods=['GET'])
@login_required
def disable_access_token():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    try:
        success = rd_api.disable_access_token()
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to disable access token"})
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

def load_torrents():
    if os.path.exists('config/torrents.json'):
        with open('config/torrents.json', 'r') as f:
            return json.load(f)
    return []

def save_torrents(torrents):
    with open('config/torrents.json', 'w') as f:
        json.dump(torrents, f)

def start_download(rd_api, torrent_id):
    rd_api.start_download(torrent_id)

def check_feeds():
    rd_api = RealDebridAPI(config.get_rd_api_key())
    added_torrents = load_torrents()
    for feed in config.get_feeds():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            if 'magnet' in entry.link:
                magnet_link = entry.link
                if magnet_link not in added_torrents:
                    response = rd_api.add_magnet(magnet_link)
                    if 'id' in response:
                        torrent_id = response['id']
                        start_download(rd_api, torrent_id)
                        added_torrents.append(magnet_link)
                        logging.info(f"Added magnet link: {magnet_link}")  # Log added magnet links
    save_torrents(added_torrents)

def retry_with_exponential_backoff(func, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            wait_time = 2 ** retries
            logging.error(f"Error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
    raise Exception("Max retries exceeded")

if __name__ == '__main__':
    init_auth()
    scheduler.add_job(check_feeds, 'interval', hours=1)
    scheduler.start()
    app.run(host='0.0.0.0', port=10500)

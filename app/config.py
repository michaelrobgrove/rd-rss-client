import json
import os

class Config:
    def __init__(self):
        self.config_file = 'config/settings.json'
        self.load_config()

    def load_config(self):
        if not os.path.exists('config'):
            os.makedirs('config')
        if not os.path.exists(self.config_file):
            self.config = {'feeds': [], 'rd_api_key': '', 'api_methods': {}}
            self.save_config()
        else:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def get_feeds(self):
        return self.config['feeds']

    def add_feed(self, url):
        if url not in self.config['feeds']:
            self.config['feeds'].append(url)
            self.save_config()

    def remove_feed(self, index):
        if 0 <= index < len(self.config['feeds']):
            self.config['feeds'].pop(index)
            self.save_config()

    def get_rd_api_key(self):
        return self.config['rd_api_key']

    def set_rd_api_key(self, key):
        self.config['rd_api_key'] = key
        self.save_config()

    def get_api_methods(self):
        return self.config['api_methods']

    def set_api_methods(self, methods):
        self.config['api_methods'] = methods
        self.save_config()

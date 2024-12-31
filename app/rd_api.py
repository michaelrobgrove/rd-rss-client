import requests
import time
import logging

class RealDebridAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.real-debrid.com/rest/1.0'

    def add_magnet(self, magnet_link):
        if self.is_duplicate(magnet_link):
            return {"error": "Duplicate torrent"}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        data = {'magnet': magnet_link}
        response = self.retry_with_exponential_backoff(
            lambda: requests.post(f'{self.base_url}/torrents/addMagnet', headers=headers, data=data)
        )
        return response.json()

    def get_torrents(self):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = self.retry_with_exponential_backoff(
            lambda: requests.get(f'{self.base_url}/torrents/instantAvailability', headers=headers)
        )
        if response.status_code == 404:
            logging.error("404 Not Found: The endpoint URL may be incorrect.")
            return []
        return response.json()

    def is_duplicate(self, magnet_link):
        torrents = self.get_torrents()
        for torrent in torrents:
            if torrent['magnet'] == magnet_link:
                return True
        return False

    def start_download(self, torrent_id):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = self.retry_with_exponential_backoff(
            lambda: requests.post(f'{self.base_url}/torrents/selectFiles/{torrent_id}', headers=headers, data={'files': 'all'})
        )
        return response.json()

    def retry_with_exponential_backoff(self, func, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                response = func()
                if response.status_code == 401:
                    self.refresh_token()
                else:
                    return response
            except Exception as e:
                wait_time = 2 ** retries
                logging.error(f"Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
        raise Exception("Max retries exceeded")

    def refresh_token(self):
        # Placeholder for token refresh logic
        logging.info("Refreshing API token...")
        # Implement token refresh mechanism here
        pass

import requests

class RealDebridAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.real-debrid.com/rest/1.0'

    def add_magnet(self, magnet_link):
        if self.is_duplicate(magnet_link):
            return {"error": "Duplicate torrent"}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        data = {'magnet': magnet_link}
        response = requests.post(f'{self.base_url}/torrents/addMagnet', 
                               headers=headers, 
                               data=data)
        return response.json()

    def get_torrents(self):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(f'{self.base_url}/torrents/instantAvailability', 
                              headers=headers)
        return response.json()

    def is_duplicate(self, magnet_link):
        torrents = self.get_torrents()
        for torrent in torrents:
            if torrent['magnet'] == magnet_link:
                return True
        return False

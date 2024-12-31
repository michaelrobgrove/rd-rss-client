import requests

class RealDebridAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.real-debrid.com/rest/1.0'

    def add_magnet(self, magnet_link):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        data = {'magnet': magnet_link}
        response = requests.post(f'{self.base_url}/torrents/addMagnet', 
                               headers=headers, 
                               data=data)
        return response.json()

import requests
import time
import logging
from typing import Optional, Dict, Any, List

class RealDebridAPI:
    def __init__(self, api_token: str, base_url: str = "https://api.real-debrid.com/rest/1.0"):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def check_instant_availability(self, hash_or_magnet: str) -> Optional[Dict[str, Any]]:
        """
        Check instant availability for a specific hash/magnet instead of empty endpoint
        """
        # Clean the hash/magnet input
        if hash_or_magnet.startswith('magnet:'):
            # Extract hash from magnet link
            try:
                hash_part = hash_or_magnet.split('btih:')[1].split('&')[0].lower()
            except IndexError:
                return None
        else:
            hash_part = hash_or_magnet.lower()

        try:
            response = requests.get(
                f"{self.base_url}/torrents/instantAvailability/{hash_part}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                # Hash not found or not instantly available
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            logging.error(f"Error checking instant availability: {str(e)}")
            return None

    def add_magnet(self, magnet_link: str) -> Optional[str]:
        """Add a magnet link to Real-Debrid"""
        try:
            response = requests.post(
                f"{self.base_url}/torrents/addMagnet",
                headers=self.headers,
                data={'magnet': magnet_link}
            )
            if response.status_code == 201:
                return response.json().get('id')
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error adding magnet: {str(e)}")
            return None

    def select_files(self, torrent_id: str, file_ids: List[int] = None) -> bool:
        """Select files to download"""
        try:
            data = {'files': ','.join(map(str, file_ids))} if file_ids else {'all': True}
            response = requests.post(
                f"{self.base_url}/torrents/selectFiles/{torrent_id}",
                headers=self.headers,
                data=data
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error selecting files: {str(e)}")
            return False

# Usage example
def process_torrent(api: RealDebridAPI, magnet_link: str) -> bool:
    # First check instant availability
    availability = api.check_instant_availability(magnet_link)
    
    if availability:
        logging.info("Torrent is instantly available")
    
    # Add magnet regardless of availability
    torrent_id = api.add_magnet(magnet_link)
    if not torrent_id:
        return False
        
    # Select all files by default
    return api.select_files(torrent_id)

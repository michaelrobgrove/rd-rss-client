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

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user info"""
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting user info: {str(e)}")
            return None

    def unrestrict_link(self, link: str) -> Optional[Dict[str, Any]]:
        """Unrestrict a link"""
        try:
            response = requests.post(
                f"{self.base_url}/unrestrict/link",
                headers=self.headers,
                data={'link': link}
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error unrestricting link: {str(e)}")
            return None

    def get_traffic_info(self) -> Optional[Dict[str, Any]]:
        """Get traffic information for limited hosters"""
        try:
            response = requests.get(
                f"{self.base_url}/traffic",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting traffic info: {str(e)}")
            return None

    def get_streaming_links(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get streaming links for a given file"""
        try:
            response = requests.get(
                f"{self.base_url}/streaming/transcode/{file_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting streaming links: {str(e)}")
            return None

    def get_downloads_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get user downloads list"""
        try:
            response = requests.get(
                f"{self.base_url}/downloads",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting downloads list: {str(e)}")
            return None

    def delete_download(self, download_id: str) -> bool:
        """Delete a link from downloads list"""
        try:
            response = requests.delete(
                f"{self.base_url}/downloads/delete/{download_id}",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error deleting download: {str(e)}")
            return False

    def get_supported_hosts(self) -> Optional[List[Dict[str, Any]]]:
        """Get supported hosts"""
        try:
            response = requests.get(
                f"{self.base_url}/hosts",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting supported hosts: {str(e)}")
            return None

    def get_user_settings(self) -> Optional[Dict[str, Any]]:
        """Get current user settings"""
        try:
            response = requests.get(
                f"{self.base_url}/settings",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting user settings: {str(e)}")
            return None

    def update_user_settings(self, settings: Dict[str, Any]) -> bool:
        """Update user settings"""
        try:
            response = requests.post(
                f"{self.base_url}/settings/update",
                headers=self.headers,
                data=settings
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error updating user settings: {str(e)}")
            return False

    def convert_fidelity_points(self) -> bool:
        """Convert fidelity points"""
        try:
            response = requests.post(
                f"{self.base_url}/settings/convertPoints",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error converting fidelity points: {str(e)}")
            return False

    def change_password(self) -> bool:
        """Send verification email to change the password"""
        try:
            response = requests.post(
                f"{self.base_url}/settings/changePassword",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error changing password: {str(e)}")
            return False

    def upload_avatar(self, avatar_file: bytes) -> bool:
        """Upload avatar image"""
        try:
            response = requests.put(
                f"{self.base_url}/settings/avatar",
                headers=self.headers,
                data=avatar_file
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error uploading avatar: {str(e)}")
            return False

    def delete_avatar(self) -> bool:
        """Reset user avatar"""
        try:
            response = requests.delete(
                f"{self.base_url}/settings/avatar",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error deleting avatar: {str(e)}")
            return False

    def get_server_time(self) -> Optional[Dict[str, Any]]:
        """Get server time"""
        try:
            response = requests.get(
                f"{self.base_url}/time",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting server time: {str(e)}")
            return None

    def get_server_time_iso(self) -> Optional[Dict[str, Any]]:
        """Get server time in ISO"""
        try:
            response = requests.get(
                f"{self.base_url}/time/iso",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting server time in ISO: {str(e)}")
            return None

    def disable_access_token(self) -> bool:
        """Disable current access token"""
        try:
            response = requests.get(
                f"{self.base_url}/disable_access_token",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error disabling access token: {str(e)}")
            return False

    def get_time(self) -> Optional[Dict[str, Any]]:
        """Get server time"""
        try:
            response = requests.get(
                f"{self.base_url}/time",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting time: {str(e)}")
            return None

    def get_time_iso(self) -> Optional[Dict[str, Any]]:
        """Get server time in ISO format"""
        try:
            response = requests.get(
                f"{self.base_url}/time/iso",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting time in ISO format: {str(e)}")
            return None

    def disable_access_token(self) -> bool:
        """Disable current access token"""
        try:
            response = requests.get(
                f"{self.base_url}/disable_access_token",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error disabling access token: {str(e)}")
            return False

    def get_torrents_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get user torrents list"""
        try:
            response = requests.get(
                f"{self.base_url}/torrents",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting torrents list: {str(e)}")
            return None

    def get_torrent_info(self, torrent_id: str) -> Optional[Dict[str, Any]]:
        """Get info on a specific torrent"""
        try:
            response = requests.get(
                f"{self.base_url}/torrents/info/{torrent_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting torrent info: {str(e)}")
            return None

    def get_active_torrents_count(self) -> Optional[int]:
        """Get the number of currently active torrents"""
        try:
            response = requests.get(
                f"{self.base_url}/torrents/activeCount",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json().get('count')
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting active torrents count: {str(e)}")
            return None

    def get_available_hosts(self) -> Optional[List[str]]:
        """Get available hosts"""
        try:
            response = requests.get(
                f"{self.base_url}/torrents/availableHosts",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting available hosts: {str(e)}")
            return None

    def add_torrent(self, torrent_file: bytes) -> Optional[str]:
        """Add a torrent file"""
        try:
            response = requests.put(
                f"{self.base_url}/torrents/addTorrent",
                headers=self.headers,
                data=torrent_file
            )
            if response.status_code == 201:
                return response.json().get('id')
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error adding torrent: {str(e)}")
            return None

    def add_magnet(self, magnet_link: str) -> Optional[str]:
        """Add a magnet link"""
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
        """Select files of a torrent"""
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

    def delete_torrent(self, torrent_id: str) -> bool:
        """Delete a torrent from torrents list"""
        try:
            response = requests.delete(
                f"{self.base_url}/torrents/delete/{torrent_id}",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error deleting torrent: {str(e)}")
            return False

    def get_supported_hosts(self) -> Optional[List[Dict[str, Any]]]:
        """Get supported hosts"""
        try:
            response = requests.get(
                f"{self.base_url}/hosts",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting supported hosts: {str(e)}")
            return None

    def get_host_status(self) -> Optional[Dict[str, Any]]:
        """Get status of hosters"""
        try:
            response = requests.get(
                f"{self.base_url}/hosts/status",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting host status: {str(e)}")
            return None

    def get_supported_regex(self) -> Optional[List[str]]:
        """Get all supported regex"""
        try:
            response = requests.get(
                f"{self.base_url}/hosts/regex",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting supported regex: {str(e)}")
            return None

    def get_supported_regex_folder(self) -> Optional[List[str]]:
        """Get all supported regex for folder links"""
        try:
            response = requests.get(
                f"{self.base_url}/hosts/regexFolder",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting supported regex for folder links: {str(e)}")
            return None

    def get_supported_domains(self) -> Optional[List[str]]:
        """Get all supported domains"""
        try:
            response = requests.get(
                f"{self.base_url}/hosts/domains",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting supported domains: {str(e)}")
            return None

    def get_user_settings(self) -> Optional[Dict[str, Any]]:
        """Get current user settings"""
        try:
            response = requests.get(
                f"{self.base_url}/settings",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting user settings: {str(e)}")
            return None

    def update_user_settings(self, settings: Dict[str, Any]) -> bool:
        """Update user settings"""
        try:
            response = requests.post(
                f"{self.base_url}/settings/update",
                headers=self.headers,
                data=settings
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error updating user settings: {str(e)}")
            return False

    def convert_fidelity_points(self) -> bool:
        """Convert fidelity points"""
        try:
            response = requests.post(
                f"{self.base_url}/settings/convertPoints",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error converting fidelity points: {str(e)}")
            return False

    def change_password(self) -> bool:
        """Send verification email to change the password"""
        try:
            response = requests.post(
                f"{self.base_url}/settings/changePassword",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error changing password: {str(e)}")
            return False

    def upload_avatar(self, avatar_file: bytes) -> bool:
        """Upload avatar image"""
        try:
            response = requests.put(
                f"{self.base_url}/settings/avatar",
                headers=self.headers,
                data=avatar_file
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error uploading avatar: {str(e)}")
            return False

    def delete_avatar(self) -> bool:
        """Reset user avatar"""
        try:
            response = requests.delete(
                f"{self.base_url}/settings/avatar",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error deleting avatar: {str(e)}")
            return False

    def get_server_time(self) -> Optional[Dict[str, Any]]:
        """Get server time"""
        try:
            response = requests.get(
                f"{self.base_url}/time",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting server time: {str(e)}")
            return None

    def get_server_time_iso(self) -> Optional[Dict[str, Any]]:
        """Get server time in ISO"""
        try:
            response = requests.get(
                f"{self.base_url}/time/iso",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error getting server time in ISO: {str(e)}")
            return None

    def disable_access_token(self) -> bool:
        """Disable current access token"""
        try:
            response = requests.get(
                f"{self.base_url}/disable_access_token",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            logging.error(f"Error disabling access token: {str(e)}")
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

import os
import re
import requests
import yaml
from urllib.parse import urlparse
from datetime import datetime

class StreamUpdater:
    def __init__(self, config_file='config.yml'):
        self.config = self.load_config(config_file)
        self.create_output_folder()
        
    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def create_output_folder(self):
        if not os.path.exists(self.config['output']['folder']):
            os.makedirs(self.config['output']['folder'])
    
    def fetch_url_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_m3u8_link(self, content):
        matches = re.findall(self.config['pattern'], content)
        return matches[0] if matches else None
    
    def generate_m3u8_content(self, channel_name, stream_url):
        return f"""#EXTM3U
#EXTINF:-1 tvg-id="{channel_name}" tvg-name="{channel_name}" group-title="Live",{channel_name}
{stream_url}
"""
    
    def save_stream_file(self, channel_name, content):
        filename = os.path.join(self.config['output']['folder'], f"{channel_name}.m3u8")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {channel_name}.m3u8")
    
    def update_all_channels(self):
        for channel in self.config['channels']:
            print(f"Processing {channel['name']}...")
            content = self.fetch_url_content(channel['url'])
            if content:
                m3u8_link = self.extract_m3u8_link(content)
                if m3u8_link:
                    m3u8_content = self.generate_m3u8_content(channel['name'], m3u8_link)
                    self.save_stream_file(channel['name'], m3u8_content)
                else:
                    print(f"No m3u8 link found for {channel['name']}")
            else:
                print(f"Failed to fetch content for {channel['name']}")
        
        # Create playlist file
        self.create_playlist_file()
    
    def create_playlist_file(self):
        playlist_path = os.path.join(self.config['output']['folder'], "playlist.m3u8")
        with open(playlist_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for channel in self.config['channels']:
                filename = f"{channel['name']}.m3u8"
                f.write(f"#EXTINF:-1 tvg-id=\"{channel['name']}\",{channel['name']}\n")
                f.write(f"{filename}\n")
        print("Created playlist.m3u8")

if __name__ == "__main__":
    updater = StreamUpdater()
    updater.update_all_channels()

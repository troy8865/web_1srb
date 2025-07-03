import os
import re
import requests
import json
from urllib.parse import urlparse
from datetime import datetime

class StreamUpdater:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.create_output_folder()
        
    def load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_output_folder(self):
        folder_path = self.config['output']['folder']
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")
    
    def fetch_url_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_m3u8_link(self, content):
        matches = re.findall(self.config['pattern'], content)
        if matches:
            return matches[0]
        print("No m3u8 link found in content")
        return None
    
    def generate_m3u8_content(self, channel_name, stream_url):
        return f"""#EXTM3U
#EXTINF:-1 tvg-id="{channel_name}" tvg-name="{channel_name}" group-title="Live",{channel_name}
{stream_url}
"""
    
    def save_stream_file(self, channel_name, content):
        filename = os.path.join(self.config['output']['folder'], f"{channel_name}.m3u8")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated: {filename}")
    
    def update_all_channels(self):
        print("\nStarting channel updates...")
        for channel in self.config['channels']:
            print(f"\nProcessing channel: {channel['name']}")
            print(f"Fetching URL: {channel['url']}")
            
            content = self.fetch_url_content(channel['url'])
            if not content:
                continue
                
            m3u8_link = self.extract_m3u8_link(content)
            if not m3u8_link:
                continue
                
            print(f"Found stream URL: {m3u8_link}")
            m3u8_content = self.generate_m3u8_content(channel['name'], m3u8_link)
            self.save_stream_file(channel['name'], m3u8_content)
        
        self.create_playlist_file()
        print("\nAll channels processed!")
    
    def create_playlist_file(self):
        playlist_path = os.path.join(self.config['output']['folder'], "playlist.m3u8")
        with open(playlist_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for channel in self.config['channels']:
                filename = f"{channel['name']}.m3u8"
                f.write(f"#EXTINF:-1 tvg-id=\"{channel['name']}\",{channel['name']}\n")
                f.write(f"{filename}\n")
        print(f"\nCreated master playlist: {playlist_path}")

if __name__ == "__main__":
    print("Starting stream updater...")
    updater = StreamUpdater()
    updater.update_all_channels()
    print("Stream updater completed!")

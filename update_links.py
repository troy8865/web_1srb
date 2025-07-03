import streamlink
import os
import json
import sys
from datetime import datetime

def generate_stream_info(stream_info, url):
    """Generate HLS stream info text"""
    info_parts = ['#EXT-X-STREAM-INF:']
    
    if stream_info.program_id:
        info_parts.append(f'PROGRAM-ID={stream_info.program_id},')
    if stream_info.bandwidth:
        info_parts.append(f'BANDWIDTH={stream_info.bandwidth},')
    if stream_info.codecs:
        codecs = ','.join(stream_info.codecs)
        info_parts.append(f'CODECS="{codecs}",')
    if stream_info.resolution:
        info_parts.append(f'RESOLUTION={stream_info.resolution[0]}x{stream_info.resolution[1]}')
    
    return ''.join(info_parts) + f'\n{url}\n'

def process_channel(channel, output_dirs):
    """Process single channel stream"""
    try:
        streams = streamlink.streams(channel['url'])
        if not streams or 'best' not in streams:
            raise Exception("No streams found")

        playlists = streams['best'].multivariant.playlists
        master_content = []
        best_content = None
        max_resolution = 0

        # Process all available qualities
        for playlist in sorted(playlists, key=lambda x: x.stream_info.resolution[1] if x.stream_info.resolution else 0, reverse=True):
            if playlist.stream_info.video == "audio_only":
                continue
                
            stream_url = playlist.uri
            stream_info = generate_stream_info(playlist.stream_info, stream_url)
            
            master_content.append(stream_info)
            
            # Track best quality
            current_res = playlist.stream_info.resolution[1] if playlist.stream_info.resolution else 0
            if current_res > max_resolution:
                max_resolution = current_res
                best_content = stream_info

        # Generate final content
        if master_content:
            version = streams['best'].multivariant.version or 3
            header = f'#EXTM3U\n#EXT-X-VERSION:{version}\n'
            
            # Save master playlist (all qualities)
            master_path = os.path.join(output_dirs['master'], f"{channel['slug']}.m3u8")
            with open(master_path, 'w') as f:
                f.write(header + ''.join(master_content))
            
            # Save best quality
            best_path = os.path.join(output_dirs['best'], f"{channel['slug']}.m3u8")
            with open(best_path, 'w') as f:
                f.write(header + best_content)
            
            print(f"✅ {channel['name']} updated (Best: {max_resolution}p)")
            return True

    except Exception as e:
        print(f"❌ {channel['name']} failed: {str(e)}")
        # Clean up failed channels
        for dir_type in ['master', 'best']:
            file_path = os.path.join(output_dirs[dir_type], f"{channel['slug']}.m3u8")
            if os.path.exists(file_path):
                os.remove(file_path)
        return False

def main(config_path):
    with open(config_path) as f:
        config = json.load(f)

    # Create output directories
    output_dirs = {
        'root': config['output']['folder'],
        'master': os.path.join(config['output']['folder'], config['output']['masterFolder']),
        'best': os.path.join(config['output']['folder'], config['output']['bestFolder'])
    }
    
    for dir_path in output_dirs.values():
        os.makedirs(dir_path, exist_ok=True)

    # Process all channels
    success_count = 0
    for channel in config['channels']:
        if channel.get('enabled', True):
            if process_channel(channel, output_dirs):
                success_count += 1

    # Generate timestamp file
    with open(os.path.join(output_dirs['root'], 'last_update.txt'), 'w') as f:
        f.write(datetime.now().isoformat())

    print(f"\n🎉 {success_count}/{len(config['channels']} channels updated successfully")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stream_updater.py <config.json>")
        sys.exit(1)
    main(sys.argv[1])

import json
import os
import requests
from datetime import datetime

# 1. JSON faylını oxu
with open('channels.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. 'm3u8_files' qovluğunu yarat (əgər yoxdursa)
os.makedirs('m3u8_files', exist_ok=True)

# 3. Hər kanal üçün ayrı .m3u8 faylı yarat və linkləri yenilə
for channel in data['channels']:
    if channel['auto_update']:
        try:
            response = requests.get(channel['url'], timeout=10)
            if response.status_code == 200:
                # Fayl adı: kanal adından boşluqları silib `.m3u8` əlavə et (məs: "İctimai_TV.m3u8")
                filename = f"m3u8_files/{channel['name'].replace(' ', '_')}.m3u8"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"✅ {channel['name']} linki yeniləndi: {filename}")
            else:
                print(f"❌ {channel['name']} linki işləmir (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Xəta ({channel['name']}): {str(e)}")

# 4. Ümumi M3U faylı yarat (bütün kanallar üçün)
with open('all_channels.m3u', 'w', encoding='utf-8') as f:
    f.write("#EXTM3U\n")
    for channel in data['channels']:
        f.write(f"#EXTINF:-1, {channel['name']}\n")
        f.write(f"{channel['url']}\n\n")

print("✨ Bütün eməliyyatlar tamamlandı!")

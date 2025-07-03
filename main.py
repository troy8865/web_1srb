import os
import re
import sys
import json
import requests
from slugify import slugify
from tqdm import tqdm
from urllib.parse import urljoin

def get_stream_url(url, pattern):
    try:
        r = requests.get(url, timeout=10)
        results = re.findall(pattern, r.text)
        if results:
            return results[0].replace("\\", "")
        else:
            print(f"Nəticə tapılmadı: {url}")
            return None
    except Exception as e:
        print(f"Xəta: {e}")
        return None

def playlist_text(url):
    text = ""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.iter_lines():
                try:
                    line = line.decode(errors="ignore")
                except:
                    continue
                if not line:
                    continue
                if line[0] != "#":
                    text += urljoin(url, line)
                else:
                    text += line
                text += "\n"
    except:
        return ""
    return text

def save_if_changed(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Qovluğu avtomatik yarat
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == content:
                print(f"Fayl dəyişməyib: {path}")
                return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"Fayl YENİLƏNDİ: {path}")

def main():
    if len(sys.argv) < 2:
        print("Istifadə: python main.py config.json")
        return

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        config = json.load(f)

    output_folder = config["output"].get("folder", "streams")
    pattern = config.get("pattern", r"https?:\\/\\/[^\\s\"']+\\.m3u8")

    for ch in tqdm(config["channels"]):
        name = ch["name"]
        url = ch["url"]
        stream_url = get_stream_url(url, pattern)
        if stream_url:
            playlist = playlist_text(stream_url)
            if playlist:
                file_path = os.path.join(output_folder, slugify(name.lower()) + ".m3u8")
                save_if_changed(file_path, playlist)
            else:
                print(f"{name} üçün playlist boşdur.")
        else:
            print(f"{name} üçün stream tapılmadı.")

    print("\nSTREAMS QOVLUĞUNDAKI FAYLLAR:")
    if os.path.exists(output_folder):
        for f in os.listdir(output_folder):
            print(" -", f)
    else:
        print("Qovluq yaradılmadı ya da fayl yoxdur.")

if __name__ == "__main__":
    main()

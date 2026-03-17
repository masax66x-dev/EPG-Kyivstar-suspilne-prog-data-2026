import urllib.request
import json
import csv
from datetime import datetime
import time
import os

channels_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTable/channels.json'
web_csv_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTableWeb/multichannel_max_epg.csv'
native_csv_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTable/ProgramTable/multichannel_max_epg.csv'

# Load valid channels
with open(channels_path, 'r', encoding='utf-8') as f:
    channels = json.load(f)

# Ensure Pershyi HD is in the list
if not any(c['id'] == '55efdb72e4b0781039bc0340' for c in channels):
    channels.append({"id": "55efdb72e4b0781039bc0340", "name": "Pershyi HD"})

ranges = [
    ("20260301", "20260310"), # Mar 1 - Mar 10
    ("20260311", "20260320"), # Mar 11 - Mar 20
    ("20260321", "20260330"), # Mar 21 - Mar 30
    ("20260331", "20260409"), # Mar 31 - Apr 9
]

all_programs = []
existing = set() # Prevent overlapping duplicates

for channel in channels:
    channel_id = channel['id']
    channel_name = channel['name']
    channel_count = 0
    
    print(f"Fetching full EPG for {channel_name}...")
    
    for r_start, r_end in ranges:
        url = f"https://clients.production.vidmind.com/vidmind-stb-ws/livechannels/{channel_id}/epg?from={r_start}&to={r_end}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        try:
            res = urllib.request.urlopen(req, timeout=15)
            data = json.loads(res.read().decode('utf-8'))
            
            for group in data:
                if 'programList' in group:
                    for p in group['programList']:
                        start_dt = datetime.fromtimestamp(p['start'] / 1000)
                        end_dt = datetime.fromtimestamp(p['finish'] / 1000)
                        duration = p.get('duration', (p['finish'] - p['start']) // 60000)
                        title = p.get('title', '').replace('"', '""')
                        desc = p.get('desc', '').replace('"', '""')
                        
                        if ',' in title or '"' in title: title = f'"{title}"'
                        if ',' in desc or '"' in desc: desc = f'"{desc}"'
                        c_name = channel_name
                        if ',' in c_name or '"' in c_name: c_name = f'"{c_name}"'
                        
                        start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                        end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                        uid = f"{channel_id}_{start_str}"
                        if uid not in existing:
                            all_programs.append(f"{c_name},{title},{start_str},{end_str},{duration},{desc}")
                            existing.add(uid)
                            channel_count += 1
        except Exception as e:
            print(f"  -> Error on range {r_start}-{r_end}: {e}")
        time.sleep(0.5)
        
    print(f"  -> Total: {channel_count} programs")

print(f"\nTotal extraction complete: {len(all_programs)} total unique programs found.")

header = "Channel Name,Program Title,Start Time,End Time,Duration (mins),Description\n"

# Rewrite Web CSV
try:
    with open(web_csv_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write("\n".join(all_programs))
        f.write("\n")
    print(f"Successfully saved to {web_csv_path}")
except Exception as e:
    print(f"Failed to write to web csv: {e}")

# Rewrite Native CSV
try:
    with open(native_csv_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write("\n".join(all_programs))
        f.write("\n")
    print(f"Successfully saved to {native_csv_path}")
except Exception as e:
    print(f"Failed to write to native csv: {e}")

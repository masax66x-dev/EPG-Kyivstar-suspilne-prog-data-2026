import urllib.request
import json
import csv
from datetime import datetime
import time

channels_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTable/channels.json'
csv_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTableWeb/multichannel_max_epg.csv'

with open(channels_path, 'r', encoding='utf-8') as f:
    channels = json.load(f)

# Keep track of existing program IDs (Channel + Start Time) to avoid overlaps
existing = set()
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if len(row) >= 3:
            existing.add(f"{row[0]}_{row[2]}")

print(f"Loaded {len(existing)} existing program slots.")

all_new_programs = []
added_count = 0

for channel in channels:
    # Always include the original hardcoded Pershy HD channel from previous step
    pass

# We should make sure we process the specific hardcoded 'Pershyi HD' channel as well
channels.append({"id": "55efdb72e4b0781039bc0340", "name": "Pershyi HD"})

for channel in channels:
    channel_id = channel['id']
    channel_name = channel['name']
    
    url = f"https://clients.production.vidmind.com/vidmind-stb-ws/livechannels/{channel_id}/epg?from=20260316&to=20260331"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    print(f"Fetching future EPG for {channel_name}...")
    try:
        res = urllib.request.urlopen(req, timeout=15)
        data = json.loads(res.read().decode('utf-8'))
        
        c = 0
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
                    
                    uid = f"{channel_name}_{start_str}"
                    if uid not in existing:
                        all_new_programs.append(f"{c_name},{title},{start_str},{end_str},{duration},{desc}")
                        existing.add(uid)
                        c += 1
                        added_count += 1
                        
        print(f"  -> Added {c} new future programs")
    except Exception as e:
        print(f"  -> Error: {e}")
    time.sleep(1)

if added_count > 0:
    with open(csv_path, 'a', encoding='utf-8') as f:
        f.write("\n".join(all_new_programs))
        f.write("\n")
    print(f"\nSuccessfully appended {added_count} new future programs to Web CSV!")
    
    # Also update the native Xcode App CSV so they stay in sync
    native_csv_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTable/ProgramTable/multichannel_max_epg.csv'
    with open(native_csv_path, 'a', encoding='utf-8') as f:
        f.write("\n".join(all_new_programs))
        f.write("\n")
    print(f"Successfully appended {added_count} new future programs to Xcode App CSV!")
else:
    print("No new future programs found.")

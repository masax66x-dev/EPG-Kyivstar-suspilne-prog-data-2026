import urllib.request
import json
from datetime import datetime

url = "https://clients.production.vidmind.com/vidmind-stb-ws/livechannels/55efdb72e4b0781039bc0340/epg?from=20260316&to=20260324"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

print(f"Fetching {url}")
try:
    res = urllib.request.urlopen(req, timeout=10)
    data = json.loads(res.read().decode('utf-8'))
    
    count = 0
    max_dt = None
    for group in data:
        if 'programList' in group:
            for p in group['programList']:
                dt = datetime.fromtimestamp(p['finish'] / 1000)
                if not max_dt or dt > max_dt:
                    max_dt = dt
                count += 1
                
    print(f"Fetched {count} programs.")
    if max_dt:
        print(f"Latest Program recorded: {max_dt}")
except Exception as e:
    print(f"Error: {e}")

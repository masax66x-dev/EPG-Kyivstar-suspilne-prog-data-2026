import urllib.request
import json
from datetime import datetime

# Pershyi HD
channel_id = "55efdb72e4b0781039bc0340"
url = f"https://client-api.kyivstar.ua/v1/epg/programs?channelId={channel_id}&dateFrom=2026-03-16T00:00:00&dateTo=2026-03-24T00:00:00"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    res = urllib.request.urlopen(req, timeout=10)
    data = json.loads(res.read().decode('utf-8'))
    print(f"API Returned {len(data.get('programs', []))} programs.")
    if data.get('programs'):
        last = data['programs'][-1]
        print(f"Last program time: {last.get('startDate')}")
except Exception as e:
    print(f"Error: {e}")

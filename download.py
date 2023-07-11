import subprocess
from curl_cffi import requests
import json
from datetime import datetime

channel_info = "https://kick.com/api/v1/channels/infrared"
live_link_check = "https://kick.com/api/v2/channels/infrared/livestream"


response = requests.get(live_link_check,  impersonate="chrome101")
response_json_str = json.dumps(response.json(), indent=4)
response_json_obj = json.loads(response_json_str)

if response_json_obj['data'] is None:
    print("Stream is not live")
else:
    print(response_json_str)
    stream_start = datetime.strptime(response_json_obj['data']['created_at'][0:19], "%Y-%m-%dT%H:%M:%S")
    current_time_utc = datetime.utcnow()
    stream_duration = current_time_utc - stream_start
    print("Stream has been live for " + str(stream_duration))
    max_record_time = 60 * 60 * 3
    script_run_interval = 60 * 5
    # This script is triggered once every 5 minutes but we only need to record once every 3 hours
    if (stream_duration.total_seconds() % max_record_time > script_run_interval ):
        print("Job already running")
        exit()
    playback_url = response_json_obj['data']['playback_url']
    datestr = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = datestr + ' - ' + response_json_obj['data']['slug'] + ' [' + str(response_json_obj['data']['id']) + '].ts'
    subprocess.call(['streamlink', playback_url, 'best', '-o', file_name], timeout=max_record_time + 60)

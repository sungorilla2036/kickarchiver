import subprocess
from curl_cffi import requests
import json
from datetime import datetime

channel_info = "https://kick.com/api/v1/channels/realvyok"
live_link_check = "https://kick.com/api/v2/channels/realvyok/livestream"


response = requests.get(live_link_check,  impersonate="chrome101")
response_json_str = json.dumps(response.json(), indent=4)
response_json_obj = json.loads(response_json_str)

if response_json_obj['data'] is None:
    print("Stream is not live")
else:
    print(response_json_str)
    playback_url = response_json_obj['data']['playback_url']
    datestr = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = datestr + ' - ' + response_json_obj['data']['slug'] + ' [' + response_json_obj['data']['id'] + '].ts'
    timeout_sec = 60 * 60 * 3
    subprocess.call(['streamlink', playback_url, 'best', '-o', file_name], timeout=timeout_sec)

import subprocess
from curl_cffi import requests
import json
from datetime import datetime
import os
import urllib.parse

job_start_time = datetime.now()
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
    max_record_time = 60 * 60 * 2.75
    script_run_interval = 60 * 5
    # This script is triggered once every 5 minutes but we only need to record once every 2.75 hours
    if (stream_duration.total_seconds() % max_record_time > script_run_interval ):
        print("Job already running")
        exit()
    playback_url = response_json_obj['data']['playback_url']
    datestr = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = datestr + ' - ' + response_json_obj['data']['slug'] + ' [' + str(response_json_obj['data']['id']) + '].ts'

    try:
        subprocess.call(['streamlink', playback_url, 'best', '-o', file_name], timeout=max_record_time + 60)
    except subprocess.TimeoutExpired:
        print("Max recording time reached")

    max_job_duration = 60 * 60 * 5.5
    job_duration = datetime.now() - job_start_time
    remaining_time = max_job_duration - job_duration.total_seconds()

    accesskey = os.environ['accesskey']
    secret = os.environ['secret']
    bucketname = os.environ['bucketname']
    # Upload to archive.org
    # curl -g --location --header 'x-archive-queue-derive:0' --header 'x-amz-auto-make-bucket:1' --header "authorization: LOW $accesskey:$secret" --upload-file "$file" http://s3.us.archive.org/"$bucketname"/"$fileNameEncoded"
    subprocess.call([
        'curl', 
        '-g', 
        '--location', 
        '--header', 
        'x-archive-queue-derive:0', 
        '--header', 
        'x-amz-auto-make-bucket:1', 
        '--header', 
        f"authorization: LOW {accesskey}:{secret}", 
        '--upload-file', 
        file_name, 
        f"http://s3.us.archive.org/{bucketname}/{urllib.parse.quote(file_name)}"
        ], timeout=remaining_time)

    job_duration = datetime.now() - job_start_time
    remaining_time = max_job_duration - job_duration.total_seconds()
    
    bucketname = os.environ['S3_BUCKET_NAME']
    # Clear secondary archive
    # aws s3 rm s3://"$bucketname" --recursive
    subprocess.call([
        'aws', 
        's3', 
        'rm',  
        f"s3://{bucketname}"
        '--recursive'
        ], timeout=remaining_time)
    
    job_duration = datetime.now() - job_start_time
    remaining_time = max_job_duration - job_duration.total_seconds()
    # Upload to secondary archive
    # aws s3 cp "$file" s3://"$bucketname"
    subprocess.call([
        'aws', 
        's3', 
        'cp', 
        file_name, 
        f"s3://{bucketname}"
        ], timeout=remaining_time)

import requests as rq
import os
import json
import time
import random
import multiprocessing

with open("./ping_list.json", "r") as f:
    _ping_list = json.load(f)

if os.path.exists('network_log.json'):
    with open('network_log.json','r') as f:
        try:
            network_log = json.load(f)
        except:
            print("corrupted file, starting over!")
            network_log = []
else:
    network_log = []

def check_response(ping_entry):
    url = ping_entry['url']
    index = ping_entry['url_index']
    error = None
    error_message = None
    resp_code = -1
    resp_ok = False
    resp_time = -1

    try:
        res = rq.get(url, timeout=5.0)
        resp_time = res.elapsed.total_seconds()
        resp_code = res.status_code
        resp_code = res.status_code
        resp_ok = res.status_code == rq.codes.ok

    except Exception as e:
        error = type(e).__name__
        error_message = repr(e)

    return {'url':url, 'url_index':index, 'response_code':resp_code, 'response_ok':resp_ok, 'response_time':resp_time, 'unixtime':int(time.time()), 'error':error, 'error_message':error_message}

while True:
    time.sleep(random.random()+1)

    with multiprocessing.Pool(processes=len(_ping_list)) as pool:
        results = pool.map_async(check_response, _ping_list)
        results.wait()
        items = results.get()
        network_log += items
        print(json.dumps(items, indent=2))
    with open('network_log.json', 'w') as outfile:
        outfile.write(json.dumps(network_log, indent=2))

import requests as rq
import os
import json
import time
import random
import multiprocessing

ping_list = [
    'http://www.google.com',
    'http://www.facebook.com',
    'http://www.apple.com',
    'http://www.microsoft.com'
]

if os.path.exists('network.log'):
    with open('network.log','r') as f:
        try:
            network_log = json.load(f)
        except:
            print("corrupted file, starting over!")
            network_log = []
else:
    network_log = []

def check_response(url):
    error = None
    try:
        resp_time = rq.get(url, timeout=5.0).elapsed.total_seconds()
    except Exception as e:
        resp_time = -1
        error = type(e).__name__

    return {'url':url, 'response_time':resp_time, 'unixtime':int(time.time()), 'error':error}

while True:
    time.sleep(random.random()+1)

    with multiprocessing.Pool(processes=len(ping_list)) as pool:
        results = pool.map_async(check_response, ping_list)
        results.wait()
        items = results.get()
        network_log += items
        print(json.dumps(items, indent=2))
    with open('network.log', 'w') as outfile:
        outfile.write(json.dumps(network_log, indent=2))

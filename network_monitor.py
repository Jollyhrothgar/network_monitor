import requests as rq
import os
import json
import time
import random
import multiprocessing
import ast
import datetime as dt

with open("./ping_list.json", "r") as f:
    _ping_list = json.load(f)

good_requests = 0
error_requests = 0
archive_file = 'network_data.log' # a file with a json dict per line to allow for appending without loading the whole file

if os.path.exists(archive_file):
    print("appending data to ", archive_file)
    input("press enter to continue, or kill the program!")
else:
    print("no file {} exists. Starting over.".format(archive_file))

def check_response(ping_entry):
    url = ping_entry['url']
    index = ping_entry['url_index']
    error = None
    error_message = None
    resp_code = -1
    resp_ok = False
    resp_str_length = -1
    resp_time = -1

    try:
        res = rq.get(url, timeout=5.0)
        resp_time = res.elapsed.total_seconds()
        resp_code = res.status_code
        resp_code = res.status_code
        resp_ok = res.status_code == rq.codes.ok
        resp_str_length = len(res.text)

    except Exception as e:
        error = type(e).__name__
        error_message = repr(e)

    return {'url':url, 'url_index':index, 'response_code':resp_code, 'response_ok':resp_ok, 'response_time':resp_time, 'unixtime':int(time.time()), 'error':error, 'error_message':error_message, 'resp_str_length':resp_str_length}

get_counter = 0
while True:
    sleep_interval = random.random()
    time.sleep(sleep_interval)

    with multiprocessing.Pool(processes=len(_ping_list)) as pool:
        results = pool.map_async(check_response, _ping_list)
        results.wait()
        items = results.get()
        good_requests += sum(1 if item['response_time'] > 0 else 0 for item in items)
        error_requests += sum(1 if item['response_time'] < 0 else 0 for item in items) 

    with open(archive_file, 'a+') as outfile:
        for line in items:
            outfile.write("{}\n".format(json.dumps(line)))

    print("Network sample {} at {}, interval {:.2f}, good {}, bad {}".format(get_counter, dt.datetime.now() , sleep_interval, good_requests, error_requests), end='\r')
    get_counter += 1

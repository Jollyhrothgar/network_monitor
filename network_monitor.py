"""
@author: michael.beaumier@gmail.com

Usage:
    Currently just runs forever from the command line logging network data, one
    json-dict at a time to the output file. 

    The current architecture has each thread write out to the
    network_traffic.log once all are finished (either the thread times out or
    it finishes).

Improvements:
    * Use lock-files or similar mechanism (maybe a queue?) to run threads in
    parallel asynchronously to write out to a log file. The multiprocessing
    library has some caveats with this and uses its own implementation of
    queue.

    * Implement command-line driven interface
"""

import requests as rq
import sys
import os
import json
import time
import random
import multiprocessing
import ast
import datetime as dt
import threading

def check_response(ping_entry):
    url = ping_entry['url']
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

    return {'url':url, 'response_code':resp_code, 'response_ok':resp_ok, 'response_time':resp_time, 'utc_datetime':str(dt.datetime.utcnow()), 'unixtime':int(time.time()), 'error':error, 'error_message':error_message, 'resp_str_length':resp_str_length}

class MainThread(threading.Thread):
    def __init__(self, archive_file='network_data.log', ping_list='./ping_list.json'):
        self._number_of_iterations = 0
        self._archive_file = archive_file
        self._ping_list = ping_list

        super(MainThread, self).__init__()
        self._stop_event = threading.Event()
        if os.path.exists(self._archive_file):
            print("appending data to ", self._archive_file)
            input("press enter to continue, or kill the program!")
        else:
            print("no file {} exists. Starting over.".format(self._archive_file))
        
        with open(self._ping_list, "r") as f:
            self._ping_list = json.load(f)

        self.good_requests = 0
        self.error_requests = 0

    def run(self):
        while not self._stop_event.is_set():
            sleep_interval = random.random()
            time.sleep(sleep_interval)

            with multiprocessing.Pool(processes=len(self._ping_list)) as pool:
                results = pool.map_async(check_response, self._ping_list)
                results.wait()
                items = results.get()
                self.good_requests += sum(1 if item['response_time'] > 0 else 0 for item in items)
                self.error_requests += sum(1 if item['response_time'] < 0 else 0 for item in items) 

            with open(self._archive_file, 'a+') as outfile:
                for line in items:
                    outfile.write("{}\n".format(json.dumps(line)))

            print("Network sample {} at {}, interval {:.2f}, good {}, bad {}".format(self._number_of_iterations, dt.datetime.now() , sleep_interval, self.good_requests, self.error_requests), end='\r')
            self._number_of_iterations += 1

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

if __name__ == '__main__':
    main = MainThread()
    try:
        main.run()
    except KeyboardInterrupt:
        print("Closing Program")
        main.stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

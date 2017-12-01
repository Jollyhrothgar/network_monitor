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

import requests 
import sys
import os
import json
import time
import random
import multiprocessing
import ast
import datetime as dt
import threading
import uuid
import speedtest

def sample_network(ping_entry):

    samples = []
    uid = str(uuid.uuid1())
    num_samples = 5
    time_out = 1

    for _ in range(num_samples):
        out = {
            'url':ping_entry['url'],
            'unixtime':None,
            'errors':None,
            'resp_code':None,
            'resp_length':None,
            'resp_times':None,
            'date_string':None,
            'error_text':None,
            'error_type':None,
            'ok':1,
            'uuid':uid,
        }
        out['unixtime'] = int(time.time())
        out['datetime'] = str(dt.datetime.utcnow())
        try:
            res = requests.get(out['url'], timeout=time_out)
            out['resp_time'] = res.elapsed.total_seconds()
            out['resp_code'] = res.status_code
            out['resp_length'] = len(res.text)
            out['error_text'] = 'no_error'
            out['error_type'] = 'no_error'

        except requests.exceptions.Timeout as e:
            out['resp_time'] = -1
            out['resp_code'] = -1
            out['resp_length'] = -1
            out['error_text'] = 'out_of_time_{}'.format(time_out)
            out['error_type'] = type(e).__name__
            out['ok'] = 0

        except Exception as e:
            error = type(e).__name__
            error_message = repr(e)
            out['resp_time'] = -1
            out['resp_code'] = -1
            out['resp_length'] = -1
            out['error_text'] = repr(e) 
            out['error_type'] = type(e).__name__
            out['ok'] = 0
            
        samples.append(out)
    return samples

def check_response(ping_entry):
    url = ping_entry['url']
    error = None
    error_message = None
    resp_code = -1
    resp_ok = False
    resp_str_length = -1
    resp_time = -1

    try:
        res = requests.get(url, timeout=5.0)
        resp_time = res.elapsed.total_seconds()
        resp_code = res.status_code
        resp_code = res.status_code
        resp_ok = res.status_code == requests.codes.ok
        resp_str_length = len(res.text)

    except Exception as e:
        error = type(e).__name__
        error_message = repr(e)

    return {'url':url, 'response_code':resp_code, 'response_ok':resp_ok, 'response_time':resp_time, 'utc_datetime':str(dt.datetime.utcnow()), 'unixtime':int(time.time()), 'error':error, 'error_message':error_message, 'resp_str_length':resp_str_length}

class MainThread(threading.Thread):
    def __init__(self, archive_file='network_data.log', speed_file='speed_file.log', ping_list='./ping_list.json'):
        self._number_of_iterations = 0
        self._archive_file = archive_file
        self._ping_list = ping_list
        self._speed_file = speed_file

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

        # Main Process
        while not self._stop_event.is_set():
            # Ping Websites
            with multiprocessing.Pool(processes=len(self._ping_list)) as pool:
                results = pool.map_async(sample_network, self._ping_list)
                results.wait()
                items = results.get()

                for packet in items:
                    for request in packet:
                        if request['ok'] == 1:
                            self.good_requests += 1
                        else:
                            self.error_requests += 1

            # Download/Upload Speed Test
            servers = []
            s = speedtest.Speedtest()
            s.get_servers(servers)
            s.get_best_server()
            s.download()
            s.upload()
            results_dict = s.results.dict()
            speed = {}
            for field in results_dict:
                if field == 'server':
                    for server_field in results_dict[field]:
                        speed[server_field] = results_dict[field][server_field]
                else:
                    speed[field] = results_dict[field]

            # Archive Upload/Download Data
            with open(self._speed_file, 'a+') as outfile:
                outfile.write("{}\n".format(json.dumps(speed)))

            # Archive Ping Data
            with open(self._archive_file, 'a+') as outfile:
                for packet in items:
                    for request in packet:
                        outfile.write("{}\n".format(json.dumps(request)))

            print("Network sample {} at {}, good {}, bad {}".format(
                    self._number_of_iterations, 
                    dt.datetime.now() , 
                    self.good_requests, 
                    self.error_requests
                ), 
                end='\r'
            )
            
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

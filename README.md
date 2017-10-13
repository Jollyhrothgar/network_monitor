# Introduction

This small tool can be used from the command line to monitor ping response time
to an arbitrary number of websites. It will capture network statistics and run
forever.

Everything gets saved into network\_log.json which is a json file containing the
fields (example):

* "url": "http://www.google.com",
* "url\_index": 0,
* "response\_code": 200,
* "response\_ok": true,
* "response\_time": 0.195535,
* "unixtime": 1507915442,
* "error": null,
* "error\_message": null

# Usage

<code>
:~> python3 ./network\_monitor.py
</code>

# Visualization

See the jupyter notebook NetworkTraffic

# TODO

Add command-line customization for differnet logs - we may want to run the
monitor different logs and then keep the data in the repo.

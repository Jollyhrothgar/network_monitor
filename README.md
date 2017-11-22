# Introduction

This small tool can be used from the command line to monitor ping response time
to an arbitrary number of websites. It will capture network statistics and run
forever.

All data is logged to network\_data.log. Just run the script to generate a
few entries and investigate. The format is a json-string per line.

# Usage

<code>
:~> python3 ./network\_monitor.py
</code>

# Visualization

See the jupyter notebook NetworkTraffic

# TODO

Add command-line customization for differnet logs - we may want to run the
monitor different logs and then keep the data in the repo.

* Logfile output redirect CLI

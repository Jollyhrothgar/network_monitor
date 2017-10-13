# Introduction

This small tool can be used from the command line to monitor ping response time
to an arbitrary number of websites. It will capture network statistics and run
forever.

Everything gets saved into network.log which is a json file containing the
fields:

* url (string, http://domainname.com)
* response\_time (float, seconds, -1 if error state)
* unixtime (when request was initiated)
* error (null, or the network exception)

# Usage

<code>
:~> python3 ./network\_monitor.py
</code>


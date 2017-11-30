import speedtest
import json

def new_number(start=0, step=1):
    while True:
        yield(start)
        start += step


servers = []
# If you want to test against a specific server
# servers = [1234]
num = new_number()

print("Step {}".format(next(num)))
s = speedtest.Speedtest()
print("Step {}".format(next(num)))
s.get_servers(servers)
print("Step {}".format(next(num)))
s.get_best_server()
print("Step {}".format(next(num)))
s.download()
print("Step {}".format(next(num)))
s.upload()

print('done')

results_dict = s.results.dict()
print(json.dumps(results_dict, indent=2))

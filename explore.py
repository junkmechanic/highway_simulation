import pickle
from collections import namedtuple

CallInfo = namedtuple('CallInfo', ['id', 'base_station', 'init_interval',
                                   'position', 'duration', 'speed', 'status'])

picklefile = "call-data-81.pickle"
with open(picklefile, 'rb') as pfile:
    global call_data
    call_data = pickle.load(pfile)

#print(len(call_data))
csvfile = 'simulation-data.csv'
picklefile = 'call-data-81.pickle'
call_data = []
with open(picklefile, 'rb') as pfile:
    call_data = pickle.load(pfile)
with open(csvfile, 'a') as outf:
    for info in call_data:
        outf.write(','.join([str(item) for item in info]) + '\n')

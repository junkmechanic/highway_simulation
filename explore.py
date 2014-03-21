import pickle
from collections import namedtuple

CallInfo = namedtuple('CallInfo', ['id', 'base_station', 'init_interval',
                                   'duration', 'speed', 'status'])

picklefile = "call-data-601.pickle"
with open(picklefile, 'rb') as pfile:
    global call_data
    call_data = pickle.load(pfile)

print(len(call_data))

import os
import sys
import pickle
from collections import namedtuple

CallInfo = namedtuple('CallInfo', ['id', 'base_station', 'init_interval',
                                   'position', 'duration', 'speed', 'status'])

call_data = []


def explore(picklefile):
    global call_data
    with open(picklefile, 'rb') as pfile:
        call_data = pickle.load(pfile)


def convert(picklefile):
    fname, exten = os.path.splitext(picklefile)
    csvfile = fname + '.csv'
    call_data = []
    with open(picklefile, 'rb') as pfile:
        call_data = pickle.load(pfile)
    with open(csvfile, 'a') as outf:
        for info in call_data:
            outf.write(','.join([str(item) for item in info]) + '\n')


if __name__ == '__main__':
    #convert(sys.argv[1])
    explore(sys.argv[1])

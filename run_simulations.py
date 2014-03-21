#!/usr/bin/env python
import subprocess
import argparse
from collections import namedtuple
import pickle

SEEDS = [
    7925, 601, 3755, 6553, 9928, 1588, 8988, 8286, 6500, 1007, 9415, 4671,
    1397, 4274, 4201, 1179, 9077, 5353, 1805, 8050, 2824, 8447, 4057, 5756,
    9446, 6017, 1102, 3173, 734, 9880, 789, 8457, 9894, 5924, 7542, 4328,
    5356, 3644, 4113, 4221, 88, 8314, 8144, 2686, 3572, 1454, 5047, 5946,
    3058, 2905
]

NUM_SIM = 02

CallInfo = namedtuple('CallInfo', ['id', 'base_station', 'init_interval',
                                   'duration', 'speed', 'status'])

# Parse Arguments
parser = argparse.ArgumentParser(description='Enter options for simulation.')
parser.add_argument('-n', '--num', action='store', type=int,
                    help='No. of simulations to run')
args = parser.parse_args()
if args.num:
    NUM_SIM = args.num

pipes = []

# Run all simulations
for i in range(NUM_SIM):
    outfile = 'simulation-' + str(SEEDS[i]) + '.log'
    cmd = './highway_simulator.py -s ' + str(SEEDS[i]) +\
          ' -t ' + str(50) + ' >' + outfile + ' 2>simulation-errors.log'
    print "Running : " + cmd
    pipes.append(subprocess.Popen(cmd, shell=True))

exit_codes = [p.wait() for p in pipes]

#Convert data to csv
csvfile = 'simulation-data.csv'
for i in range(NUM_SIM):
    picklefile = 'call-data-' + str(SEEDS[i]) + '.pickle'
    call_data = []
    with open(picklefile, 'rb') as pfile:
        call_data = pickle.load(pfile)
    with open(csvfile, 'a') as outf:
        for info in call_data:
            outf.write(','.join([str(item) for item in info]) + '\n')

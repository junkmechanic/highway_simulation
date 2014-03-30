#!/usr/bin/env python
#import subprocess
import argparse
from collections import namedtuple
import pickle
from highway_simulator_hcr_v2 import simulate_hcr

SEEDS = [
    7925, 601, 3755, 6553, 9928, 1588, 8988, 8286, 6500, 1007, 9415, 4671,
    1397, 4274, 4201, 1179, 9077, 5353, 1805, 8050, 2824, 8447, 4057, 5756,
    9446, 6017, 1102, 3173, 734, 9880, 789, 8457, 9894, 5924, 7542, 4328,
    5356, 3644, 4113, 4221, 88, 8314, 8144, 2686, 3572, 1454, 5047, 5946,
    3058, 2905
]

NUM_SIM = 02

SIM_TIME = 400

HANDOVR = 1

verbosity = 0

CallInfo = namedtuple('CallInfo', ['id', 'base_stations', 'init_interval',
                                   'position', 'duration', 'speed', 'status'])

# Parse Arguments
parser = argparse.ArgumentParser(description='Enter options for simulation.')
parser.add_argument('-r', '--runs', action='store', type=int,
                    help='No. of simulations to run')
parser.add_argument('-t', '--time', action='store', type=float,
                    help='Time of each simulation ')
parser.add_argument('-n', '--num', action='store', type=int,
                    help='Number of channels reserved for handover')
parser.add_argument('-v', '--verbose', action='count',
                    help='Verbosity level on the commandline ouput')
args = parser.parse_args()
if args.runs:
    NUM_SIM = args.runs
if args.time:
    SIM_TIME = args.time
if args.num:
    HANDOVR = args.num
if args.verbose:
    verbosity = args.verbose

# Running processes simultaneously is not working for some reason. It errors
# out with some problem or the other. So will run each simulation after the
# other.
#pipes = []

blocked = []
dropped = []

# Run all simulations
for i in range(NUM_SIM):
    stats = simulate_hcr(SEEDS[i], SIM_TIME, True, HANDOVR, verbosity)
    blocked.append(stats['blocked'] / float(stats['total']) * 100.0)
    dropped.append(stats['dropped'] / float(stats['total']) * 100.0)
    #dropped.append(stats['dropped'] / float(stats['total']) * 100.0)


print "Blocked %"
print blocked
print str(sum(blocked) / float(len(blocked)))
print "Dropped %"
print dropped
print str(sum(dropped) / float(len(dropped)))

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

#!/usr/bin/env python
#import subprocess
import argparse
from collections import namedtuple
import pickle
from highway_simulator import simulate

SEEDS = [
    7925, 601, 3755, 6553, 9928, 1588, 8988, 8286, 6500, 1007, 9415, 4671,
    1397, 4274, 4201, 1179, 9077, 5353, 1805, 8050, 2824, 8447, 4057, 5756,
    9446, 6017, 1102, 3173, 734, 9880, 789, 8457, 9894, 5924, 7542, 4328,
    5356, 3644, 4113, 4221, 88, 8314, 8144, 2686, 3572, 1454, 5047, 5946,
    3058, 2905
]

NUM_SIM = 02

SIM_TIME = 400

CallInfo = namedtuple('CallInfo', ['id', 'base_station', 'init_interval',
                                   'position', 'duration', 'speed', 'status'])

# Parse Arguments
parser = argparse.ArgumentParser(description='Enter options for simulation.')
parser.add_argument('-n', '--num', action='store', type=int,
                    help='No. of simulations to run')
parser.add_argument('-t', '--time', action='store', type=float,
                    help='Time of each simulation ')
args = parser.parse_args()
if args.num:
    NUM_SIM = args.num
if args.time:
    SIM_TIME = args.time

# Running processes simultaneously is not working for some reason. It errors
# out with some problem or the other. So will run each simulation after the
# other.
#pipes = []

blocked = []
dropped = []

# Run all simulations
for i in range(NUM_SIM):
    #outfile = 'simulation-' + str(SEEDS[i]) + '.log'
    #cmd = './highway_simulator.py -s ' + str(SEEDS[i]) +\
    #      ' -t ' + str(SIM_TIME) + ' >' + outfile + ' 2>simulation-errors.log'
    #print "Running : " + cmd
    #subprocess.check_call(cmd, shell=True)
    #pipes.append(subprocess.Popen(cmd, shell=True))
    stats = simulate(SEEDS[i], SIM_TIME)
    blocked.append(stats['blocked'] / float(stats['total']) * 100.0)
    dropped.append(stats['dropped'] / float(stats['total']) * 100.0)

#exit_codes = [p.wait() for p in pipes]

print blocked
print str(sum(blocked) / float(len(blocked)))
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

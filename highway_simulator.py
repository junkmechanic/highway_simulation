#!/usr/bin/python
import random
import simpy
import argparse
from collections import namedtuple

RANDOM_SEED = 21

# Statistics
blocked_calls = 0
successful_calls = 0
dropped_calls = 0
total_calls = 0

# Car speed stats
CAR_LOW = 70.0
CAR_HIGH = 110.0
CELL_LEN = 20.0

# Call duration stats
CALL_DURAION_MEAN = 119.0

NUM_CELLS = 03

# Expovariate means for each base station
base_stations_mean = {}
for n in range(NUM_CELLS):
    base_stations_mean[n] = 28.0

# Maximum number of calls in the simulation
MAX_CALLS = 4500

# Maximum simulation running time
MAX_SIM_TIME = 500

# Bollean to control simulation termination conditions
SIM_TIME_FLAG = False

# Variables for call data
CallInfo = namedtuple('CallInfo', ['init_interval', 'duration', 'speed',
                                   'status'])
call_data = []

# Parse Arguments
parser = argparse.ArgumentParser(description='Enter options for simulation.')
parser.add_argument('-c', '--calls', action='store', type=int,
                    help='No. of calls during the simulation')
parser.add_argument('-t', '--time', action='store', type=float,
                    help='The total duration of the simulation ' +
                    '[ * Takes precedence over --calls option]')
args = parser.parse_args()
if args.calls:
    MAX_CALLS = args.calls
if args.time:
    MAX_SIM_TIME = args.time
    SIM_TIME_FLAG = True


def call(env, base_stations, id, bs):
    """
    This represents a call. Following is the logical flow of this process.
    1. Decide on its own duration
    2. Decide on the speed of the car that it originates from.
    3. Request for a channel in that cell
    4. If not possible, add to blocked_calls
    5. If possible, check if handover is required
    6. If not, then hold the channel for the required duration, add to
    successful_calls
    7. If handover is required, (while handover = True), hold the current
    channel for the complete duration, then release it, change the bs to the
    next one and continue.
    """
    global blocked_calls
    global successful_calls
    global dropped_calls
    first_iter = True
    duration = random.expovariate(1 / CALL_DURAION_MEAN)
    car_speed = random.triangular(CAR_LOW, CAR_HIGH) / 3600.0
    cover_time = CELL_LEN / car_speed
    handover = True if cover_time < duration else False
    while (first_iter or handover):
        with base_stations[bs].request() as try_call:
            result = yield try_call | env.timeout(0.0)

            # if result object does not contain the Request object and this
            # was the first iteration for this call (process), that means
            # that the Resource (channel) was not free and the call has been
            # blocked
            if try_call not in result and first_iter:
                print "{:.4f} Call ID {} has been BLOCKED from BS {}".\
                      format(env.now, id, bs)
                blocked_calls += 1
                env.exit()
            elif try_call not in result and not first_iter:
                print "{:.4f} Call ID {} has been DROPPED from BS {}".\
                      format(env.now, id, bs)
                dropped_calls += 1
                env.exit()

            # re-evaluate handover
            handover = True if cover_time < duration else False
            # if handover is false, then use the channel for the call
            # duration and then release it
            if handover is False:
                print "{:.4f} Call ID {} with duration {:.3f}s with speed {}"\
                      " STARTED from BS {}".format(env.now, id, duration,
                                                   car_speed, bs)
                yield env.timeout(duration)
                print "{:.4f} Call ID {} ENDED.".format(env.now, id)
                successful_calls += 1
                env.exit()

            # if handover is true
            if handover:
                duration -= cover_time
                print "{:.4f} Call ID {} with duration {:.3f}s with speed {}"\
                      " STARTED from BS {}".format(env.now, id, duration,
                                                   car_speed, bs)
                yield env.timeout(cover_time)
                bs = 0 if bs + 1 == NUM_CELLS else bs + 1
                print "{:.4f} Call ID {} attempting a HANDOVER to BS {}".\
                      format(env.now, id, bs)
                first_iter = False


def callGenerator(env, base_stations, own_bs, finishUp):
    global total_calls
    i = 1
    while True:
        next_call = random.expovariate(1 / base_stations_mean[own_bs])
        print "{:.4f} Next call from BS {} in {:.4f}".\
              format(env.now, own_bs, next_call)
        #### TODO Still one call more than expected
        total_calls += 1
        if not SIM_TIME_FLAG and total_calls > MAX_CALLS:
            print "{:.4f} BS {} noticed calls maxed out".format(env.now,
                                                                own_bs)
            finishUp.succeed()
            break
        result = yield env.timeout(next_call) | finishUp
        if finishUp in result:
            break
        id = str(own_bs) + '-' + str(i)
        print "{:.4f} Call ID {} INITIATED from BS {}".format(env.now, id,
                                                              own_bs)
        env.process(call(env, base_stations, id, own_bs))
        i += 1


def spawner(env, base_stations, finishUp):
    for bs in range(NUM_CELLS):
        env.process(callGenerator(env, base_stations, bs, finishUp))


def timeWatch(event, env, duration):
    yield env.timeout(duration)
    print "Time over"
    event.succeed()


random.seed(RANDOM_SEED)
env = simpy.Environment()
finishUp = env.event()
base_stations = {}
for i in range(NUM_CELLS):
    base_stations[i] = simpy.Resource(env, capacity=10)
spawner(env, base_stations, finishUp)
if SIM_TIME_FLAG:
    env.run(env.process(timeWatch(finishUp, env, MAX_SIM_TIME)))
else:
    env.run()
print "Total calls = {}".format(total_calls)
print "Blocked calls = {}".format(blocked_calls)
print "Dropped calls = {}".format(dropped_calls)
print "Successful calls = {}".format(successful_calls)

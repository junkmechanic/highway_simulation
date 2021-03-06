#!/usr/bin/env python
import random
import simpy
import argparse
import pickle
from collections import namedtuple

RANDOM_SEED = 81

# Statistics
blocked_calls = 0
successful_calls = 0
dropped_calls = 0
handed_over = 0
total_calls = 0

# Car speed stats
CAR_LOW = 70.0
CAR_HIGH = 110.0
CELL_LEN = 2.0

# Call duration stats
CALL_DURAION_MEAN = 119.0

NUM_CELLS = 20

# Channels reserved for handover
HANDOVR_CHAN = 0

# Expovariate means for each base station
base_stations_mean = {
    0: 27.7, 1: 28.3, 2: 28.3, 3: 27.6, 4: 27.4, 5: 27.5, 6: 27.2, 7: 25.6,
    8: 25.1, 9: 25.2, 10: 27.5, 11: 25.4, 12: 26.5, 13: 25.1, 14: 27.4,
    15: 27.5, 16: 27.3, 17: 26.4, 18: 28.0, 19: 27.9
}
#for n in range(NUM_CELLS):
#    base_stations_mean[n] = 28.0

# Maximum number of calls in the simulation
MAX_CALLS = 4500

# Maximum simulation running time
MAX_SIM_TIME = 500

# Boolean to control simulation termination conditions
SIM_TIME_FLAG = False

# Variables for call data
CallInfo = namedtuple('CallInfo', ['id', 'base_stations', 'init_interval',
                                   'position', 'duration', 'speed', 'status'])
call_data = []

verbosity = 0


def call(env, base_stations, id, bs, init_interval):
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
    global handed_over
    global call_data

    first_iter = True

    total_duration = random.expovariate(1 / CALL_DURAION_MEAN)
    car_speed = random.triangular(CAR_LOW, CAR_HIGH) / 3600.0
    original_position = random.uniform(0.0, CELL_LEN)

    # In case of handover, the duration value needs to be reduced, hence
    # capture it in another variable. Same goes for the position.
    duration = total_duration
    position = original_position
    cover_time = (CELL_LEN - position) / car_speed
    handover = True if cover_time < duration else False
    call_status = 'Undefined'
    bs_visited = []

    while (first_iter or handover):
        if first_iter or base_stations[bs][1].capacity == 0:
            server = base_stations[bs][0]
        else:
            server = base_stations[bs][1]
        with server.request() as try_call:
            result = yield try_call | env.timeout(0.0)

            # if result object does not contain the Request object and this
            # was the first iteration for this call (process), that means
            # that the Resource (channel) was not free and the call has been
            # blocked
            if try_call not in result and first_iter:
                printf("{:.4f} Call ID {} has been BLOCKED from BS {}".
                       format(env.now, id, bs), 1)
                blocked_calls += 1
                call_status = 'Blocked'
                break
            elif try_call not in result and not first_iter:
                printf("{:.4f} Call ID {} has been DROPPED from BS {}".
                       format(env.now, id, bs), 1)
                dropped_calls += 1
                call_status = 'Dropped'
                break

            bs_visited.append(bs)

            # re-evaluate handover
            cover_time = (CELL_LEN - position) / car_speed
            handover = True if cover_time < duration else False
            # if handover is false, then use the channel for the call
            # duration and then release it
            if handover is False:
                printInitiation(env, id, duration, car_speed, bs,
                                position, first_iter)
                yield env.timeout(duration)
                printf("{:.4f} Call ID {} ENDED.".format(env.now, id), 2)
                successful_calls += 1
                call_status = 'Successful'
                if first_iter is False:
                    handed_over += 1
                    call_status += '+HandedOver'
                break
                #env.exit()

            # if handover is true
            if handover:
                printInitiation(env, id, duration, car_speed, bs,
                                position, first_iter)
                duration -= cover_time
                yield env.timeout(cover_time)
                bs = 0 if bs + 1 == NUM_CELLS else bs + 1
                printf("{:.4f} Call ID {} attempting a HANDOVER to BS {}".
                       format(env.now, id, bs), 1)
                if first_iter is False:
                    handed_over += 1
                first_iter = False
                # Now update position to 0.0 to indicate that it is the
                # starting of the next cell
                position = 0.0

    # Store call data
    call_data.append(CallInfo(id, bs_visited, init_interval, original_position,
                              total_duration, car_speed, call_status))


def printInitiation(env, id, duration, car_speed, bs, position, first_iter):
    if first_iter:
        printf("{:.4f} Call ID {} with duration {:.3f}s with speed {}"
               " STARTED from BS {} at position {}".
               format(env.now, id, duration, car_speed, bs, position), 1)
    else:
        printf("{:.4f} Call ID {} with duration {:.3f}s with speed {}"
               " HANDED-OVER to BS {}".
               format(env.now, id, duration, car_speed, bs), 1)


def callGenerator(env, base_stations, own_bs, finishUp):
    global total_calls
    i = 1
    while True:
        next_call = random.expovariate(1 / base_stations_mean[own_bs])
        #next_call = random.gammavariate(0.976, 27.6)
        printf("{:.4f} Next call from BS {} in {:.4f}".
               format(env.now, own_bs, next_call), 3)
        result = yield env.timeout(next_call) | finishUp
        if finishUp in result:
            break
        id = str(own_bs) + '-' + str(i)
        printf("{:.4f} Call ID {} INITIATED from BS {}".format(env.now, id,
                                                               own_bs), 2)
        total_calls += 1
        env.process(call(env, base_stations, id, own_bs, next_call))
        if not SIM_TIME_FLAG and total_calls > MAX_CALLS:
            printf("{:.4f} BS {} noticed calls maxed out".format(env.now,
                                                                 own_bs), 3)
            finishUp.succeed()
            break
        i += 1


def spawner(env, base_stations, finishUp):
    for bs in range(NUM_CELLS):
        env.process(callGenerator(env, base_stations, bs, finishUp))


def timeWatch(event, env, duration):
    yield env.timeout(duration)
    event.succeed()
    printf("{:.4f} No more calls. Waiting for the live calls to end".
           format(env.now), 3)


def simulate_hcr(SEED, SIM_TIME, TIME_FLAG=True, HANDOVR=1, verbose=0):
    global RANDOM_SEED, SIM_TIME_FLAG, MAX_SIM_TIME, HANDOVR_CHAN
    initialize(SEED, SIM_TIME, TIME_FLAG, HANDOVR, verbose)
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    finishUp = env.event()
    base_stations = {}
    # Each base station has two types of resources (channels), the first one
    # for calls originating within that BS and the other for calls being
    # handed-over from the previous BS.
    for i in range(NUM_CELLS):
        base_stations[i] = (simpy.Resource(env, capacity=(10 - HANDOVR_CHAN)),
                            simpy.Resource(env, capacity=HANDOVR_CHAN))
    spawner(env, base_stations, finishUp)
    if SIM_TIME_FLAG:
        env.process(timeWatch(finishUp, env, MAX_SIM_TIME))
        # If you pass a process to run() of class Environment, the simulation
        # will exit once that process is over, regardless of all the other
        # processes defined for the environment
    env.run()
    printf("Total calls = {}".format(total_calls))
    printf("Blocked calls = {}".format(blocked_calls))
    printf("Dropped calls = {}".format(dropped_calls))
    printf("Handed-Over calls = {}".format(handed_over))
    printf("Successful calls = {}".format(successful_calls))

    # Store the call data in a pickle
    picklefile = 'call-data-' + str(RANDOM_SEED) + '.pickle'
    with open(picklefile, 'wb') as pfile:
        pickle.dump(call_data, pfile)

    return({'total': total_calls, 'blocked': blocked_calls,
            'dropped': dropped_calls, 'handed': handed_over,
            'success': successful_calls})


def initialize(SEED, SIM_TIME, TIME_FLAG, HANDOVR, verbose):
    global RANDOM_SEED, SIM_TIME_FLAG, MAX_SIM_TIME, HANDOVR_CHAN
    global blocked_calls, successful_calls, dropped_calls, handed_over,\
        total_calls, verbosity
    RANDOM_SEED = SEED
    SIM_TIME_FLAG = TIME_FLAG
    MAX_SIM_TIME = SIM_TIME
    HANDOVR_CHAN = HANDOVR
    verbosity = verbose
    blocked_calls, successful_calls, dropped_calls, handed_over,\
        total_calls = 0, 0, 0, 0, 0


def printf(toprint, verbose=0):
    #global verbosity
    with open('simulation.log', 'a') as logfile:
        logfile.write(toprint + '\n')
    if verbosity >= verbose:
        print toprint


if __name__ == '__main__':
    # Parse Arguments
    parser = argparse.ArgumentParser(description='Options for simulation.')
    parser.add_argument('-c', '--calls', action='store', type=int,
                        help='No. of calls during the simulation')
    parser.add_argument('-t', '--time', action='store', type=float,
                        help='The total duration of the simulation ' +
                        '[ * Takes precedence over --calls option]')
    parser.add_argument('-n', '--num', action='store', type=int,
                        help='Number of channels reserved for handover')
    parser.add_argument('-s', '--seed', action='store', type=int,
                        help='Random seed for the simulation')
    parser.add_argument('-v', '--verbose', action='count',
                        help='Verbosity level on the commandline ouput')
    args = parser.parse_args()
    if args.calls:
        MAX_CALLS = args.calls
    if args.time:
        MAX_SIM_TIME = args.time
        SIM_TIME_FLAG = True
    if args.num:
        HANDOVR_CHAN = args.num
    if args.seed:
        RANDOM_SEED = args.seed
    if args.verbose:
        verbosity = args.verbose

    simulate_hcr(RANDOM_SEED, MAX_SIM_TIME, SIM_TIME_FLAG, HANDOVR_CHAN,
                 verbosity)

This is a simulation of a highway with 20 radio cells that cater to the call
being made by cars on the highway

Run run_simulations.py for multiple simulation runs.
For single simulation, use highway_simulator.py
Use -h or --help for options to give on the commandline.
Verbosity is specified with number of 'v'. For example, `-v`, `-vv`, `-vvv`.

Running highway_simulator will generate a log file and a pickle file. The
pickle file contains data on all calls made in that simulation. To view this
file, run `python explore.py call-data-RAND.pickle`, where RAND is a number as
indicated by the filename. This will generate a csv file.

run_simulations.py runs multiple simulations. Hence, a csv file is
automatically generated which contains call data from all the simulations
combined. For individual simulations, one can run explore.py as mentioned
above.

hcr files are for simulating handover channel reservation scheme. The files
without the hcr suffix are with fixed channel reservation scheme. hcr_v2 is to
provision using the other channels as well for handover calls apart from the
channels that are dedicated for handover.

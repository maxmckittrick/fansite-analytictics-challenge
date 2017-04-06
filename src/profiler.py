#path mapping for run_features and input/output files

import cProfile
import run_features

cProfile.run('run_features.run("./log_input/log.txt", "./log_output/hosts.txt", "./log_output/hours.txt", "./log_output/resources.txt", "./log_output/blocked.txt")')

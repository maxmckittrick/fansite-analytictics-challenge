#process log for input file (1) and output files (4)

import argparse
import run_features

parser = argparse.ArgumentParser(description='Process hits from a server log.')
parser.add_argument('input_server_log',
    help='Text file containing log of server requests.')
parser.add_argument('output_hosts',
    help='Output file for the 10 most active hosts/IP addresses that have accessed the site.')
parser.add_argument('output_hours',
    help='Output file for the top 10 resources in bandwidth consumption on the site.')
parser.add_argument('output_resources',
    help='Output file for the top 10 busiest 60-minute periods on the site (not necessarily from the top of the hour).')
parser.add_argument('output_blocked',
    help='Output file for blocked users and details of rejected login requests.')
args = parser.parse_args()

#get features for each input/output argument
run_features.run(
    args.input_server_log,
    args.output_hosts,
    args.output_hours,
    args.output_resources,
    args.output_blocked)

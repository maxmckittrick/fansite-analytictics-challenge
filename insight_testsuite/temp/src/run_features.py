#feature implementation for features 1-4, allowing more features to be added in future

import feature1
import feature2
import feature3
import feature4
import read_input_data

def run(input_server_log, output_hosts, output_hours, output_resources, output_blocked):

    logf = open("errors.txt", "w") # error handling, no input errors detected in provided server log
    log_reader = read_input_data.FileInputReader(input_server_log)
    log_reader.read()

    #feature 1
    try:
        parser1 = feature1.MostActive(
            log_reader.data,
            output_hosts,
            k=10)
        parser1.parse()
    except Exception as e:
        logf.write("Failed on Feature 1: {0}\n".format(str(e)))

    #feature 2
    try:
        parser2 = feature2.MostBandwidthResources(
            log_reader.data,
            output_resources,
            k=10)
        parser2.parse()
    except Exception as e:
        logf.write("Failed on Feature 2: {0}\n".format(str(e)))

    #feature 3
    try:
        parser3 = feature3.HighestTrafficWindows(
            log_reader.data,
            output_hours,
            k=10,
            minutes_per_bucket=60) #arbitrary 60 minute time slicde
        parser3.parse()
    except Exception as e:
        logf.write("Failed on Feature 3: {0}\n".format(str(e)))

    #feature 4
    try:
        parser4 = feature4.BlockedIPs(
            log_reader.data,
            output_blocked, #for failed and subsequent attempts in lockout window
            failed_attempts = 3,
            window_seconds = 20,
            block_minutes = 5, #reset with successful login
            failure_codes=["401"])
        parser4.parse()
    except Exception as e:
        logf.write("Failed on Feature 4: {0}\n".format(str(e)))

    logf.close() #will be empty if no errors
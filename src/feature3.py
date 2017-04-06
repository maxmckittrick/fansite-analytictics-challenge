#outputs top k (10 default) busiest 60-minute periods on the site

import text_features
import csv
import collections
from datetime import datetime,timedelta #60 minute periods do not necessarily begin on the hour
import parse_server_log

class HighestTrafficWindows(text_features.TextFeatures):

    def __init__(self, input_data, output_file, k=10, minutes_per_bucket=60):
        super(HighestTrafficWindows, self).__init__(input_data, output_file)
        self.time_to_requests = collections.Counter() #used in text_features for resource listing
        self.timezone = self._get_timezone()
        self.k = k
        self.minutes_per_bucket = minutes_per_bucket #should be 60

    def _get_timezone(self):
        try:
            return self.server_log[0].timezone #all server log timezones are the same
        except:
            return "+0000" #if no timezone listed

    def _data_to_string(self, line):
        timestring, hit_count = line[0].strftime('%d/%b/%Y:%H:%M:%S'), str(line[1])
        return timestring+' '+self.timezone+','+hit_count

    def _time_slice(self): #bucket for creating 60-minute time periods for activity measurement
        try:
            initial_cutoff = self.server_log[0].timestamp
        except IndexError:
            return #in case the log doesn't have any timestamps

        hits_per_bucket = 1
        l, r = 0, 0
        max_time = self.server_log[-1].timestamp
        #l and r are pointers, loop is advanced by 1 second each tick.
        #l and r are incremented until they both are contained in the new time slice
        #should complete in linear time for total number of logs
        #my testing indicates this is the bottleneck of the 4 features (parallelization could solve this problem)
        while initial_cutoff <= max_time:
            while self.server_log[l].timestamp < initial_cutoff:
                l += 1
                hits_per_bucket -= 1
            final_cutoff = initial_cutoff + timedelta(minutes = self.minutes_per_bucket)
            while True: #loop for counting inside each time slice
                r += 1
                hits_per_bucket += 1
                if r >= self.server_log_len or self.server_log[r].timestamp > final_cutoff:
                    r -= 1
                    hits_per_bucket -= 1
                    break
            self.time_to_requests[initial_cutoff] = hits_per_bucket
            initial_cutoff += timedelta(seconds = 1)

    def _parser(self):
        self._time_slice()
        output = self._filter_top_k(self.time_to_requests, self.k)
        output.sort(key=lambda x: x[0]) #order buckets by time
        output.sort(key=lambda x: x[1], reverse=True) #order buckets in descending frequency
        self._write_output(output, self._data_to_string) #final output to file
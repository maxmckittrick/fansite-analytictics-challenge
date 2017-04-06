#text_features is used to extract features from logs and output data as strings to the specified output_file

import csv
import read_server_log

class TextFeatures(object):
    def _init_(self, server_log, output_file):
        self.server_log=server_log
        self.output_file=output_file
        self.server_log_len = len(server_log) #accepts both test log file (small) and actual log file (large)

    def _filter_top_k(self, data, k):
        return data.most_common(k) #accepts a collections counter and a limit k, returns top k elements in data using heapsort

    def _write_output(self, output_data, data_to_string=str):
    #_write_output accepts data from an iterable object into the output_file specified at construction
    #accepts as an argument output_data, a generic iterable, and a method data_to_string, which converts each item in the object into a string
        with open(self.output_file, 'w') as f_output:
            for item in output_data:
                f_output.write(data_to_string(item)+"\n")
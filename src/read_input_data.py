#data input for csv

import csv
import parse_server_log

class FileInputReader(object):
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = [] #data is appended for each line in the server log

    def read(self):
        with open(self.input_file, 'rb') as f_input:
            csv_input = csv.reader(f_input, delimiter=' ')
            for row in csv_input:
                log_line = parse_server_log.ServerLog(row)
                self.data.append(log_line)
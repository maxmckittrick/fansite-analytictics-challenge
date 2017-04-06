#outputs top k (10 default) most active hosts/IPs that have accessed the site

import text_features
import collections
import csv
import parse_server_log

class MostActive(text_features.TextFeatures):

    def __init__(self, input_data, output_file, k=10):
        super(MostActive, self).__init__(input_data, output_file)
        self.hosts_to_hits = collections.Counter() #used in text_features for host listing
        self.k = k

    def _data_to_string(self, line):
        return line[0]+","+str(line[1])

    def _parse_input(self):
        for log_line in self.server_log:
            self.hosts_to_hits[log_line.host] = self.hosts_to_hits.get(log_line.host, 0) + 1

    def _parser(self):
        self._parse_input()
        output = self._filter_top_k(self.hosts_to_hits, self.k)
        output.sort(key=lambda x: x[0]) #order hosts alphabetically
        output.sort(key=lambda x: x[1], reverse=True) #order hosts in descending frequency
        self._write_output(output, self._data_to_string) #final output to file
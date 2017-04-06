#outputs top k (10 default) resources on the site by bandwidth consumption

import text_features
import collections
import csv
import parse_server_log

class MostBandwidthResources(base_feature.BaseFeature):

    def __init__(self, input_data, output_file, k=10):
        super(MostBandwidthResources, self).__init__(input_data, output_file)
        self.resources_to_bandwidth = collections.Counter() #used in text_features for resource listing
        self.k = k

    def _data_to_string(self, line):
        return line[0]

    def _parse_input(self):
        for log_line in self.server_log:
            self.resources_to_bandwidth[log_line.resource] = self.resources_to_bandwidth.get(log_line.resource, 0) + log_line.bytes

    def _parser(self):
        self._parse_input()
        output = self._filter_top_k(self.resources_to_bandwidth, self.k)
        output.sort(key=lambda x: x[0]) #order features alphabetically
        output.sort(key=lambda x: x[1], reverse=True) #order features in descending frequency
        self._write_output(output, self._data_to_string) #final output to file
#outputs log of possible security breaches after 3 failed login attempts in a 20 second window from the same IP address and subsequent failed attempts

import text_features
from datetime import datetime,timedelta

class BlockedIPs(text_features.TextFeatures):

    def __init__(self, input_data, output_file, failed_attempts = 3, window_seconds = 20, block_minutes = 5, failure_codes=["401"]): #401 is the only failure code included in log file, others may be possible
        super(BlockedIPs, self).__init__(input_data, output_file)
        self.failed_attempts = failed_attempts #total failed attempts in window, 3 by default
        self.block_minutes = block_minutes #5 by default
        self.window_seconds = window_seconds #20 by default
        self.failure_codes = failure_codes
        self.blocked_logs = []
        self.server_log.sort(key=lambda x: x.host) #time information for each attempt by host

    def _data_to_string(self, data):
        return data.convert_to_string()

    def _failure_check(self, target_host, start_idx, current_idx, remaining_failed_attempts, time_cutoff):
        for idx in xrange(current_idx, self.server_log_len):
            if self.server_log[idx].timestamp > time_cutoff or self.server_log[idx].host != target_host: #attempts should only be checked for the same IP in the failure window
                return start_idx
            elif self.server_log[idx].response_code in self.failure_codes:
                remaining_failed_attempts -= 1
                if remaining_failed_attempts == 0:
                    return self._block_incoming_attempts(target_host, idx + 1, self.server_log[idx].timestamp + timedelta(minutes = self.block_minutes))
                else:
                    return self._failure_check(target_host, start_idx, idx + 1, remaining_failed_attempts, time_cutoff)
            else:
                return idx #successful login attempt
        return start_idx

    def _block_incoming_attempts(self, target_host, start_idx, time_cutoff):
        for idx in xrange(start_idx, self.server_log_len):
            if self.server_log[idx].timestamp > time_cutoff or self.server_log[idx].host != target_host:
                return idx 
            self.blocked_logs.append(self.server_log[idx]) #each failed attempt is logged within the timeout window
        return start_idx

    def _scan_for_first_failed_login(self):
        idx = 0
        while idx < self.server_log_len:
            log = self.server_log[idx]
            if log.response_code in self.failure_codes:
                idx = self._failure_check(log.host, idx + 1, idx + 1, self.failed_attempts - 1, log.timestamp + timedelta(seconds = self.window_seconds))
            else:
                idx += 1

    def parse(self):
        self._scan_for_first_failed_login()
        self._write_output(self.blocked_logs, self._data_to_string)
        
import collections
import pytest
import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
from datetime import datetime,timedelta
from feature4 import BlockedIPs
from gen_test_data import gen_test_data

class TestBlockedIPs:
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir

    def test_empty_input(self):
        #tests that no output is generated for an empty input
        f_output_null = self.tmpdir.join("null_output.txt")
        input_null = []
        f4_null = BlockedIPs(input_null, str(f_output_null))
        f4_null.parse()
        assert f4_null.blocked_logs == []
        assert f_output_null.read() == ""

    def test_input_data_sort(self):
        #tests that server logs are sorted by both host and time in order
        f_output_sort = self.tmpdir.join("sort_output.txt")
        input_sort = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_sort.txt'))
        f4_sort = BlockedIPs(input_sort, str(f_output_sort))
        f4_sort.parse()
        assert f4_sort.server_log[0].host == "bing.com"
        assert f4_sort.server_log[1].host == "bing.com"
        assert f4_sort.server_log[2].host == "google.com"
        assert f4_sort.server_log[3].host == "google.com"
        assert f4_sort.server_log[0].bytes == 56
        assert f4_sort.server_log[1].bytes == 1024
        assert f4_sort.server_log[2].bytes == 256
        assert f4_sort.server_log[3].bytes == 1024

    def test_blocked_requests_not_reconsidered(self):
        #test that a new timeout window is not started for failed login attempts in an existing timeout window
        f_output_not_reconsider = self.tmpdir.join("not_reconsider_output.txt")
        input_not_reconsider = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_block_not_reconsider.txt'))
        f4_not_reconsider = BlockedIPs(input_not_reconsider, str(f_output_not_reconsider))
        f4_not_reconsider.parse()
        assert len(f4_not_reconsider.blocked_logs) == 3
        #tests that first successful login attempt is not blocked
        assert f4_not_reconsider.blocked_logs[2].timestamp == datetime.strptime("01/Jul/1995:00:04:05",'%d/%b/%Y:%H:%M:%S')

    def test_failed_requests_are_reconsidered(self):
        #tests that BlockedIPs reconsiders failed attempts that do not lead to new timeout windows
        f_output_reconsider = self.tmpdir.join("reconsider_output.txt")
        input_reconsider = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_fail_reconsider.txt'))
        f4_reconsider = BlockedIPs(input_reconsider, str(f_output_reconsider))
        f4_reconsider.parse()
        assert len(f4_reconsider.blocked_logs) == 1
        assert f4_reconsider.blocked_logs[0].timestamp == datetime.strptime("01/Jul/1995:00:04:05",'%d/%b/%Y:%H:%M:%S')

    def test_additional_unsuccessful_logins_are_blocked(self):
        #tests that BlockedIPs blocks the third and subsequent connection attempts are all blocked in one timeout window
        f_output_immediate = self.tmpdir.join("immediate_output.txt")
        input_immediate = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_immediate.txt'))
        f4_immediate = BlockedIPs(input_immediate, str(f_output_immediate))
        f4_immediate.parse()
        assert len(f4_immediate.blocked_logs) == 2

    def test_successful_login_reset(self):
        #test that a successful login resets the timeout window timer
        f_output_reset = self.tmpdir.join("reset_output.txt")
        input_reset = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_reset.txt'))
        f4_reset = BlockedIPs(input_reset, str(f_output_reset))
        f4_reset.parse()
        assert len(f4_reset.blocked_logs) == 0

    def test_failed_logins_depend_on_host(self):
        #test that failed logins from different hosts do not start the timeout window for each other
        f_output_multiple_hosts = self.tmpdir.join("multiple_hosts_output.txt")
        input_multiple_hosts = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_multiple_hosts.txt'))
        f4_multiple_hosts = BlockedIPs(input_multiple_hosts, str(f_output_multiple_hosts))
        f4_multiple_hosts.parse()
        assert len(f4_multiple_hosts.blocked_logs) == 0

    def test_failed_attempts_counter(self):
        #test that the k for failed attempts can be tuned
        f_output_configure_fail = self.tmpdir.join("configure_fail_output.txt")
        input_configure_fail = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_configure_fail.txt'))
        f4_configure_fail = BlockedIPs(input_configure_fail, str(f_output_configure_fail), failed_attempts=2)
        f4_configure_fail.parse()
        assert len(f4_configure_fail.blocked_logs) == 4

    def test_block_window_minutes(self):
        #test that the size of the timeout window can be tuned
        f_output_configure_block = self.tmpdir.join("configure_block_output.txt")
        input_configure_block = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_configure_block.txt'))
        f4_configure_block = BlockedIPs(input_configure_block, str(f_output_configure_block), block_minutes=30)
        f4_configure_block.parse()
        assert len(f4_configure_block.blocked_logs) == 2

    def test_window_seconds(self):
        #test that the k for the initiatlization of the timeout window can be tuned
        f_output_configure_window = self.tmpdir.join("configure_window_output.txt")
        input_configure_window = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature4_configure_window.txt'))
        f4_configure_window = BlockedIPs(input_configure_window, str(f_output_configure_window), window_seconds=30)
        f4_configure_window.parse()
        assert len(f4_configure_window.blocked_logs) == 1
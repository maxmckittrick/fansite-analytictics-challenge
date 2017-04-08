import collections
import pytest
import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
from feature3 import HighestTrafficWindows
from gen_test_data import gen_test_data

class TestHighestTrafficWindows:
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir

    def test_empty_input(self):
        #tests that no output is generated for an empty input
        f_output_null = self.tmpdir.join("null_output.txt")
        input_null = []
        f3_null = HighestTrafficWindows(input_null, str(f_output_null), 0)
        f3_null.parse()
        assert f3_null.timezone == "+0000" # should be set to default value
        assert f3_null.time_to_requests == collections.Counter() 
        assert f_output_null.read() == ""

    def test_timezone(self):
        #tests that timezones can be parsed in the input log
        f_output_single_entry = self.tmpdir.join("single_entry_output.txt")
        input_single_entry = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature3_single_entry.txt'))
        f3_single_entry = HighestTrafficWindows(input_single_entry, str(f_output_single_entry))
        f3_single_entry.parse()
        assert f3_single_entry.timezone == "-0400" #default timezone

    def test_single_entry(self):
        #tests that a single entry input will automatically be the highest traffic window
        f_output_single_entry = self.tmpdir.join("single_entry_output.txt")
        input_single_entry = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature3_single_entry.txt'))
        f3_single_entry = HighestTrafficWindows(input_single_entry, str(f_output_single_entry))
        f3_single_entry.parse()
        assert f_output_single_entry.read() == "01/Jul/1995:00:00:01 -0400,1\n"

    def test_in_between_values(self):
        #tests that HighestTrafficWindows may occur between events
        f_output_multi_entry = self.tmpdir.join("multi_entry_output.txt")
        input_multi_entry = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature3_multi_entry.txt'))
        f3_multi_entry = HighestTrafficWindows(input_multi_entry, str(f_output_multi_entry))
        f3_multi_entry.parse()
        assert f_output_multi_entry.read() == "01/Jul/1995:00:00:01 -0400,2\n01/Jul/1995:00:00:02 -0400,1\n01/Jul/1995:00:00:03 -0400,1\n01/Jul/1995:00:00:04 -0400,1\n"

    def test_window_boundary(self):
        #tests that events exactly 0:60:00 apart are included in the same window but any events farther apart are not
        f_output_boundary = self.tmpdir.join("boundary_output.txt")
        input_boundary = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature3_boundary.txt'))
        f3_boundary = HighestTrafficWindows(input_boundary, str(f_output_boundary), k=2)
        f3_boundary.parse()
        assert f_output_boundary.read() == "01/Jul/1995:00:00:03 -0400,2\n01/Jul/1995:00:00:04 -0400,2\n"

    def test_limited_to_k(self):
        #tests that only the top k windows are returned for >k possible traffic windows
        f_output_multi_entry = self.tmpdir.join("multi_entry_output.txt")
        input_multi_entry = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature3_multi_entry.txt'))
        f3_multi_entry = HighestTrafficWindows(input_multi_entry, str(f_output_multi_entry),k=2)
        f3_multi_entry.parse()
        assert f_output_multi_entry.read() == "01/Jul/1995:00:00:01 -0400,2\n01/Jul/1995:00:00:04 -0400,1\n"

    def test_dynamic_window(self):
        #test that window may be reconfigured to be more or less than an hour
        f_output_window = self.tmpdir.join("boundary_output.txt")
        input_window = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature3_boundary.txt'))
        f3_window = HighestTrafficWindows(input_window, str(f_output_window),k=2,minutes_per_bucket=120)
        f3_window.parse()
        assert f_output_window.read() == "01/Jul/1995:00:00:03 -0400,3\n01/Jul/1995:00:00:04 -0400,2\n"

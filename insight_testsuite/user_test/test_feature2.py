import collections
import pytest
import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
from feature2 import MostBandwidthResources
from gen_test_data import gen_test_data

class TestMostBandwidthResources:
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir

    def test_empty_input(self):
        #tests that no output is generated for an empty input
        f_output_null = self.tmpdir.join("null_output.txt")
        input_null = []
        f2_null = MostBandwidthResources(input_null, str(f_output_null), 0)
        f2_null.parse()
        assert f2_null.resources_to_bandwidth == collections.Counter() 
        assert f_output_null.read() == ""

    def test_grouping(self):
        #tests that an input file with multiple logs per host is correctly grouped by MostBandwidthResources
        f_output_grouping = self.tmpdir.join("grouping_output.txt")
        input_grouping = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature2_grouping.txt'))
        f2_grouping = MostBandwidthResources(input_grouping, str(f_output_grouping), 3)
        f2_grouping.parse()
        assert f2_grouping.resources_to_bandwidth["/"] == 2048
        assert f2_grouping.resources_to_bandwidth["/correctimage.gif"] == 256
        assert f2_grouping.resources_to_bandwidth["/incorrectimage.gif"] == 112
        assert f_output_grouping.read() == '/\n/correctimage.gif\n/incorrectimage.gif\n'

    def test_breaking_ties(self):
        #tests that ties are sorted alphabetically when two resources have equal volume
        f_output_ties = self.tmpdir.join("ties_output.txt")
        input_ties = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature2_tie.txt'))
        f2_ties = MostBandwidthResources(input_ties, str(f_output_ties), 3)
        f2_ties.parse()
        assert f2_ties.resources_to_bandwidth["/correctimage.gif"] == 2048
        assert f2_ties.resources_to_bandwidth["/incorrectimage.gif"] == 2048
        assert f_output_ties.read() == '/correctimage.gif\n/incorrectimage.gif\n'

    def test_k_larger_than_data(self):
        #tests that MostActive outputs correctly when specified k most active resources is greater than the number of unique resources
        f_output_large_k = self.tmpdir.join("large_k_output.txt")
        input_large_k = gen_test_data(str(os.path.dirname(__file__) + '/../test/feature2_grouping.txt'))
        f2_large_k = MostBandwidthResources(input_large_k, str(f_output_large_k), 10)
        f2_large_k.parse()
        assert f_output_large_k.read() == '/\n/correctimage.gif\n/incorrectimage.gif\n'
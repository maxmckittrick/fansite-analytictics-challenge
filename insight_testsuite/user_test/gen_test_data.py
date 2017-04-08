#generate data for user tests

import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
from read_input_data import FileInputReader

def gen_test_data(filename):
    reader = FileInputReader(filename)
    reader.read()
    return reader.data
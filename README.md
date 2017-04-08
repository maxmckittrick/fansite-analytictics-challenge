# Insight Data Engineering Coding Challenge

## Dependencies

This project uses Python 2.7. All of the referenced modules are part of the Python standard library.

## Features

TextFeatures provided a framework for input/output and listing the top k elements from a collection. Each feature's output .txt file has a different format, so each subclasses of TextFeatures contains a specific _data_to_string() method, which formats the strings in the output file.

The same server log data is used in each feature, so the data is read into memory since file I/O is the performance bottleneck in Python. Profiling on the given log shows scanning through the data in memory is an order of magnitude faster than scanning through the file on disk. 

To scale this code for other server logs that are very large, the entire log may not be loadable in memory at once. In this case, features 1 and 2 are trivial may still be implemented since only one row needs to be read at a time.

Features 3 and 4 are parsed with respect to one or more rows at a time, so scaling these two feature extractions would need to be attempted with a specified number of server log rows input at a time.

To extract features from the server log, run_features is used. process_log may also be used with STDIN, and passes any given arguments to run_features.

All four features are isolated in try/except blocks, so each feature may fail independently. Errors are logged to a file, errors.txt. Note that no errors were found in the server log provided by Insight.

## Feature Extraction

### Feature 1

Feature 1 finds the most active hosts in the server log. A hit count is generated for each unique host in the server log. The counter object contains the hits per host, and the top k hits are extracted using heapsort.

Heapsort runs in O(n log k) time, and parsing the log takes O(n) time, so our final sort takes O(n log k) time.

### Feature 2

Similarly to Feature 1, this iterates over the server log and counts the total bytes served for each resource, using a counter object. Heapsort is used to return the top k resources served.

### Feature 3

Feature 3 uses a sliding window (60 minute default) to count how many events occur within each 60-minute period of time that contains at least one event. A counter object is used to map window start and end time to hits contained within each unique window.

The runtime of this counter is O(max(number of server logs, seconds between first and last event)), which is linear.

Two key assumptions are made for the consideration of Feature 3: time windows that begin before the first logged event are not considered, and feature granularity is limited to seconds.

### Feature 4

Feature 4 implements timeout windows for hosts. These windows may overlap in time (e.g. host A and B may be blocked independently of each other), so the server log is reconstructed by host. 

First, any failed login attempts (response code 401) are stored in a counter. If a failed login attempt is encountered, a helper function sets a time limit (default 5 minutes) and begins looking ahead in the server log. If three total failed logins occur in the same timeout window, another helper function, which logs any additional attempts by the same host over the block window, is called.

To optimize Feature 4, if a failed login is detected, instead of simply returning to our outer loop at the same index after the completion of the timeout window, the next appropriate index is considered.

Indexes may be skipped if either a successful login is detected within the 20 second interval after a failed login, nullifying the timeout window contribution of up to k-1 prior failed login attempts, or when a failed login attempt is added to the block log.

Indexes may not be skipped if three unsuccessful login attempts are not detected within a 20 second interval, e.g.; for failed login attempts at time 0, 17, 22, and 26 seconds. 

Counting from the failed login at 0 seconds and including the second failed login at 17 seconds, the second login attempt  is part of an interval with three failed login attempts (17, 22, 26). In this case, the index at 17 seconds may not be skipped as that login attempt is part of a timeout window.

### Additional Features

All parameters presented in the problem statement, including lengths of time for the activity windows in Features 3 and 4, are tuneable parameters. Note that server logs that contain events in different timezones are also considered.

## Testing

src/profiler.py runs cProfiler on all four features using the test dataset. py.test references .txt files in the /insight_testsuite/user_test folder. To run the additional tests, run py.test from the root directory.

Note that all testing was successful both in a UNIX environment (Ubuntu) and a Windows-based shell (Cygwin).

# Insight Data Engineering Coding Challenge

## Dependencies

This project uses Python 2.7. All modules used are part of the Python standard library: argparse, collections.Counter, csv, and datetime.

## Features

To facilitate feature development and abstract away the common operations for all features, I implemented a BaseFeature class. BaseFeature provides methods for reading text data, writing data back to a file, and extracting the top k elements from a collection. Since the output format is different for each feature, subclasses of BaseFeature implement a unique _data_to_string() method, which tells BaseFeature how to format the data it writes to the output file.

All features operate on server log data. As the first step in the workflow, I read the data into memory since file I/O is a performance bottleneck in Python (per my profiling on this dataset, scanning through the data in memory is ~10x faster than scanning through the file). For very large text files, it may not be possible to hold all the data in memory at once. Features 1 and 2 are trivial to implement lazily; we only need to consider one row at a time as we build up our aggregate data structure. For Features 3 and 4, we need to consider more than one row at a time; to implement this lazily, we could read in a sliding window of rows.

Features are all called from run_features. process_log accepts command line arguments and passes them to run_features. All four features are isolated in try/except blocks, so failure of one feature will not affect the others. Errors are logged to a file, errors.txt.

### Feature 1

Feature 1 finds the most active hosts in the server log. To do this, we iterate over the rows in the log and keep track of the hit count for each host in a collections.Counter object mapping host -> hits. Then we can easily extract the top k hits from the Counter using heapsort, in O(n log k) time. Since scanning the log takes O(n) time, and our final sort takes O(n log k), that gives an overall performance of O(n log k).

### Feature 2

The implementation of Feature 2 is similar to Feature 1. We iterate over the server log and keep track of the total bytes for each resource, again using a Counter object to map resource -> bytes. We again use Counter's heapsort to return the top k resources.

### Feature 3

In Feature 3, we are asked to find the busiest 60 minute window in the server log. The instructions note that a window need not begin with an event. However, the provided test case implies that the *first* window should begin with the first event, so I made that assumption.

e.g., in the test case, the log contains 10 events that occur between 00:00:01 and 00:00:15. In the test case, the expected answer has the busiest window beginning at 00:00:01, with 10 events. However, if we were to consider windows that begin *before* the first event, there would be many time windows encompassing all 10 events, e.g. 23:50:01, 23:50:02, 23:50:03, etc., on the previous day. However, given the expected output from the test case, I assume that we should not consider time windows that begin before the first logged event.

To solve this problem, I use a sliding window approach. I start with the first timestamp as my left bound, then slide my right bound out 60 minutes, keeping track of how many events I pass. I store the total number of events in this window in a Counter, mapping window start -> hits. Finally, I add one second to the left time bound (I assume second granularity for this problem) and update the left and right pointers accordingly.

The runtime of the sliding window step depends both on the number of timestamps in the log (as our left and right pointers will scan over each element in the list once) and the difference between the first and last timestamps, in seconds (as our time bound will advance through all seconds in between). Therefore this approach is O(max(number of server logs, time between first and last server log in seconds)), which is linear.

### Feature 4

In Feature 4, we need to maintain block windows for hosts. Since these block windows may overlap in time (e.g. host A could be blocked at the same time as host B), I first sort by host. We first scan through the input to find any failed login attempts (response code 401). When we encounter one, we call a helper function, which sets a time limit and begins looking ahead. If we detect three total failed logins before we reach the end of the time window, we call another helper function, which logs any additional attempts by the same host over the block window.

An important optimization to Feature 4 is to note that, once we first detect a failed login, we by necessity look ahead at the data. Instead of simply returning to our outer loop at the same index, it would be preferable to use the information we gain by looking ahead and then skipping to the next appropriate index.

There are two circumstances in which we can jump ahead:
- when we detect a successful login within the 20 second interval after a failed login. The successful login nullifies any failed logins that came before.
- when we write a login attempt to our block list

However, there are some subtle cases when we *cannot* jump ahead:
- when we fail to detect three unsuccessful login attempts within a 20 second interval. To make this clear, consider we have failed login attempts at time 0, 19, 22, and 25 seconds. We first begin searching from the failed login at 0 seconds and encounter the second failed login at 19 seconds before our interval ends. However, we must reconsider the login attempt at 19s, because it actually is part of an interval with three failed login attempts. In this case we are unable to simply skip past the 19s attempt just because we considered it already.

### Additional Features

All parameters presented in the problem statement, including lengths of time for the activity windows in Features 3 and 4, are tuneable parameters. 

## Testing

The module src/profiler.py runs cProfiler on all four features using the test dataset.

I use py.test for my unit tests. Run py.test from the root directory.

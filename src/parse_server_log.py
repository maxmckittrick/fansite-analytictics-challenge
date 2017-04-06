#time and date parser for log file

from datetime import datetime,timedelta

class ServerLog(object):

    def __init__(self, delimited_list): #space is delimiter
        self.host = delimited_list[0]
        self.timezone = self.read_timezone(delimited_list[4])
        self.timestamp = self.read_timestamp(delimited_list[3])
        self.request = delimited_list[5]
        self.resource = self.read_resource(self.request)
        self.response_code = delimited_list[6]
        self.bytes = self.read_bytes(delimited_list[7])

    def read_bytes(self, byte_string):
        try:
            bytes = int(byte_string)
        except:
            bytes = 0 #"-" is zero bytes in server log
        return bytes

    def convert_to_GMT(self, timestamp, timezone): #many server logs have multiple timezones represented, the test log does not
        ret = timestamp
        if timezone[0]=='+':
            ret+=timedelta(hours=int(timezone[1:4]))
        elif timezone[0]=='-':
            ret-=timedelta(hours=int(timezone[1:4]))
        return ret

    def process_timestamp(self, timestamp):
        ret = datetime.strptime(timestamp,'%d/%b/%Y:%H:%M:%S') #standard timestamp format in log
        return ret

    def read_timestamp(self, timestring):
        return self.process_timestamp(timestring[1:])

    def read_timezone(self, timezone): #-0000 if not specified
        return timezone[0:-1]

    def read_resource(self, request):
        request_list = request.split(' ')
        if len(request_list) == 1:
            return request
        else:
            return request_list[1]

    def convert_to_string(self): #preserves original server log for subsequent feature extraction
        ret = ""
        ret += self.host
        ret += " - - ["
        ret += self.timestamp.strftime('%d/%b/%Y:%H:%M:%S') #preserves original timestamp format
        ret += " "
        ret += self.timezone
        ret += '] "'
        ret += self.request
        ret += '" '
        ret += self.response_code
        ret += " "
        ret += str(self.bytes)
        return ret
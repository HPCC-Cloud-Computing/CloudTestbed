from datetime import datetime
import json


class LogSummary:
    def __init__(self, info_number, warning_number, error_number, debug_number, other_number, total_number):
        self.info_number = info_number
        self.warning_number = warning_number
        self.error_number = error_number
        self.debug_number = debug_number
        self.other_number = other_number
        self.total_number = total_number


class ReadLog:
    def __init__(self, file_path):
        self.file_name = file_path
        self.data = []
        with open(self.file_name, 'r') as stream_input:
            for line in stream_input:
                self.data.append(line)

    # check if start_date < end_date
    def summary_log_by_day(self, start_date=None, end_date=None):
        info_number = 0
        warning_number = 0
        error_number = 0
        debug_number = 0
        other_number = 0
        try:
            pointer = self.get_start_line(start_date)
        except self.OverDateException:
            pass
        print(pointer)
        end_line = len(self.data)
        while pointer < end_line:
            line_data = self.data[pointer]
            line_date = self.get_date_in_line(line_data)
            if line_date:
                if end_date and self.compare_date(line_date, end_date) > 0:
                    print(pointer)
                    return LogSummary(info_number, warning_number, error_number, debug_number, other_number,
                                      info_number + warning_number + error_number + debug_number + other_number)
                else:
                    log_info = line_data[20:50]
                    if "WARNING" in log_info:
                        warning_number += 1
                    elif "DEBUG" in log_info:
                        debug_number += 1
                    elif "INFO" in log_info:
                        info_number += 1
                    elif "ERROR" in log_info:
                        error_number += 1
                    else:
                        other_number += 1
            pointer+=1
        return LogSummary(info_number, warning_number, error_number, debug_number, other_number,
                          info_number + warning_number + error_number + debug_number + other_number)

    def get_start_line(self, start_date=None):
        start_counter = 0
        for line in self.data:
            line_date = self.get_date_in_line(line)
            if line_date and (not start_date or self.compare_date(line_date, start_date) >= 0):
                return start_counter
            start_counter += 1
        raise self.OverDateException()

    @staticmethod
    def get_date_in_line(line):
        if (len(line)) < 50:
            return None
        date_data = line[0: 30]
        try:
            return datetime(int(date_data[0:4]), int(date_data[5:7]), int(date_data[8:10]),
                            int(date_data[11:13]), int(date_data[14:16]), int(date_data[17:19]))
        except ValueError:
            return None

    # return 1 if date_x>date_y, 0 if date_x == date_y, -1 if date_x<date_y
    def compare_date(self, date_x, date_y):
        if date_x>date_y:
            return 1
        elif date_x==date_y:
            return 0
        else:
            return -1

    class OverDateException(Exception):
        def __init__(self):
            pass

    def test(self):
        x = self.get_date_in_line(self.data[0])
        print(x)

        # ReadLog(file_path='test.log').test()
        # print(ReadLog(file_path='n-api.log').get_start_line())

# x = ReadLog("test.log")
# start_date = datetime(2016,8,27,11,5,30)
# end_date=datetime(2016,8,27,11,9,40)
# k = x.summary_log_by_day(start_date,end_date)
# print(json.dumps(k.__dict__))
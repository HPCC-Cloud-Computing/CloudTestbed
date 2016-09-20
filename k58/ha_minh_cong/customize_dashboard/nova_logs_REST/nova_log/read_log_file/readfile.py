import datetime
from datetime import timedelta


class LogSummary:
    def __init__(self, info_number, warning_number, error_number, debug_number, other_number, total_number):
        self.info_number = info_number
        self.warning_number = warning_number
        self.error_number = error_number
        self.debug_number = debug_number
        self.other_number = other_number
        self.total_number = total_number


class ReadLog:
    log_type_list = ['INFO', 'ERROR', 'WARNING', 'DEBUG']

    def __init__(self, file_path):
        self.file_name = file_path
        self.data = []
        with open(self.file_name, 'r') as stream_input:
            for line in stream_input:
                self.data.append(line)

    class DateException:
        def __init__(self, exception_type, message):
            self.exception_type = exception_type
            self.message = message

    def get_start_date(self):
        pointer = 0
        while pointer < len(self.data):
            line_date = self.get_date_in_line(self.data[pointer])
            if line_date:
                return line_date
            pointer += 1
        raise self.OverDateException()

    def get_end_date(self, extra_precision=False):
        pointer = len(self.data) - 1
        while pointer >= 0:
            line_date = self.get_date_in_line(self.data[pointer], extra_precision)
            if line_date:
                return line_date
            pointer -= 1
        raise self.OverDateException()

    @staticmethod
    def valid_date_input(date_from_input, date_to_input):
        date_from_input_validated = 'none'
        date_to_input_validated = 'none'
        if date_from_input != 'none':
            try:
                date_from_input_validated = datetime.datetime.strptime(date_from_input, "%Y-%m-%d")
            except ValueError:
                return None, None
        if date_to_input != 'none':
            try:
                date_to_input_validated = datetime.datetime.strptime(date_to_input, "%Y-%m-%d")
            except ValueError:
                return None, None
        return date_from_input_validated, date_to_input_validated

    # check if start_date < end_date

    @staticmethod
    def get_date_range(date_from_input_validated, date_to_input_validated,
                       start_date_in_file, end_date_in_file):
        start_date = None
        end_date = None
        if date_from_input_validated != 'none' and date_to_input_validated != 'none':
            start_date = date_from_input_validated
            end_date = date_to_input_validated
        elif date_from_input_validated != 'none' and date_to_input_validated == 'none':
            start_date = date_from_input_validated
            end_date = end_date_in_file
        elif date_from_input_validated == 'none' and date_to_input_validated != 'none':
            start_date = start_date_in_file
            end_date = date_to_input_validated
        elif date_from_input_validated == 'none' and date_to_input_validated == 'none':
            start_date = start_date_in_file
            end_date = end_date_in_file
        if start_date > end_date:
            return None, None
        else:
            return start_date, end_date

    @staticmethod
    def convert_date_to_string_format(input_date):
        return str(input_date.year) + '-' + str(input_date.month) + '-' + str(input_date.day)

    """
    make date_result_array
    ...

    Parameters:
    ----------
    start_date: date_start, datetime, format Y-m-d-0-0-0
    end_date: date_end, datetime, format Y-m-d-0-0-0

    """

    @staticmethod
    def make_date_return_array(start_date, end_date):
        result_array = dict()
        date_pointer = start_date
        while date_pointer <= end_date:
            result_array[ReadLog.convert_date_to_string_format(date_pointer)+"T23:59:59"] = 0
            date_pointer += timedelta(days=1)
        return result_array

    """
    summary_log_by_day
    ...

    Parameters:
    ----------
    log_type: type of log
    start_date: date_start, string, format Y-m-d
    end_date: date_end, string, format Y-m-d

    """
    def summary_log_per_day(self, input_log_type, date_from_input, date_to_input):
        log_type_list = ['INFO', 'DEBUG', 'WARNING', 'ERROR']
        try:
            start_date_in_file = self.get_start_date()
            end_date_in_file = self.get_end_date()
        except ReadLog.OverDateException:
            raise ReadLog.DateException('info', "no data available")
        start_date_converted = ReadLog.convert_date_from_string(date_from_input)
        end_date_converted = ReadLog.convert_date_from_string(date_to_input)
        start_date, end_date = ReadLog.get_date_range(start_date_converted, end_date_converted,
                                                      start_date_in_file, end_date_in_file)
        if start_date is None or end_date is None:
            raise ReadLog.DateException('info', "no data available")
        result = ReadLog.make_date_return_array(start_date, end_date)
        try:
            pointer = self.get_start_line(start_date)
        except self.OverDateException:
            return result
        end_line = len(self.data)
        while pointer < end_line:
            line_data = self.data[pointer]
            line_date = self.get_date_in_line(line_data)
            if line_date:
                line_date_string_format = ReadLog.convert_date_to_string_format(line_date)+"T23:59:59"
                if line_date_string_format not in result:
                    return result
                else:
                    log_info = line_data[20:50]
                    if input_log_type == 'OTHER':
                        if not any(log_type in log_info for log_type in log_type_list):
                            result[line_date_string_format] += 1
                    elif input_log_type == 'ALL':
                        result[line_date_string_format] += 1
                    else:
                        if input_log_type in log_info:
                            result[line_date_string_format] += 1
            pointer += 1
        return result

    def get_start_line(self, start_date=None):
        start_counter = 0
        for line in self.data:
            line_date = self.get_date_in_line(line)
            if line_date and (start_date == 'none' or self.compare_date(line_date, start_date) >= 0):
                return start_counter
            start_counter += 1
        raise self.OverDateException()

    @staticmethod
    def get_date_in_line(line, extra_precision=False):
        if (len(line)) < 50:
            return None
        date_data = line[0: 30]
        try:
            if extra_precision:
                return datetime.datetime(int(date_data[0:4]), int(date_data[5:7]), int(date_data[8:10]),
                                         int(date_data[11:13]), int(date_data[14:16]), int(date_data[17:19]))
            else:
                return datetime.datetime(int(date_data[0:4]), int(date_data[5:7]), int(date_data[8:10]))
        except ValueError:
            return None

    # return 1 if date_x>date_y, 0 if date_x == date_y, -1 if date_x<date_y
    @staticmethod
    def compare_date(date_x, date_y):
        if date_x > date_y:
            return 1
        elif date_x == date_y:
            return 0
        else:
            return -1

    class OverDateException(Exception):
        def __init__(self):
            pass

    @staticmethod
    def add_hours_minus_and_seconds(date, hour, minute, second):
        return datetime.datetime(date.year, date.month, date.day, hour, minute, second)

    @staticmethod
    def convert_date_from_string(input_date_string,input_time_string="",extra_precision = False):
        if input_date_string != 'none':
            if not extra_precision:
                return datetime.datetime.strptime(input_date_string, "%Y-%m-%d")
            else:
                return datetime.datetime.strptime(input_date_string+':'+input_time_string, "%Y-%m-%d:%H-%M-%S")
        return input_date_string

    def summary_log_counts(self, start_date_input, end_date_input):
        result = LogSummary(0, 0, 0, 0, 0, 0)
        start_date = ReadLog.convert_date_from_string(start_date_input,'00-00-00',extra_precision=True)
        end_date = ReadLog.convert_date_from_string(end_date_input,'23-59-59',extra_precision=True)
        try:
            pointer = self.get_start_line(start_date)
        except self.OverDateException:
            return result
        end_line = len(self.data)
        while pointer < end_line:
            line_data = self.data[pointer]
            line_date = self.get_date_in_line(line_data, extra_precision=True)
            if line_date:
                if end_date!='none' and line_date > end_date:
                    return result
                else:
                    log_info = line_data[20:50]
                    if "WARNING" in log_info:
                        result.warning_number += 1
                    elif "DEBUG" in log_info:
                        result.debug_number += 1
                    elif "INFO" in log_info:
                        result.info_number += 1
                    elif "ERROR" in log_info:
                        result.error_number += 1
                    else:
                        result.other_number += 1
                    result.total_number += 1
            pointer += 1
        return result

    class LogCountInTime:
        def __init__(self, time, number_of_logs):
            self.time = time
            self.number_of_logs = number_of_logs

    @staticmethod
    def create_summary_log_with_period_result_list(period_counts, period, date_to, end_date_in_file=None):
        if date_to != 'none':
            converted_date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
            end_date = datetime.datetime(converted_date_to.year, converted_date_to.month, converted_date_to.day, 12, 0,
                                         0)
            if end_date_in_file:
                if end_date > end_date_in_file:
                    end_date = end_date_in_file
        else:
            end_date = end_date_in_file
        result_list = []
        if end_date is None:
            return result_list
        index = 0
        while index < period_counts:
            index_time = end_date - datetime.timedelta(seconds=(period_counts - (index + 1)) * period)
            result_list.append(ReadLog.LogCountInTime(index_time, 0))
            index += 1
        return result_list

    def summary_log_with_period(self, date_to, log_type, period, period_counts):
        """
        Process request with request inputs is log_type, date_to and period
        date_to will be reformat to Y-m-d-12-00-00
        """
        try:
            end_date_in_file = self.get_end_date(extra_precision=True)
        except ReadLog.OverDateException:
            result = ReadLog.create_summary_log_with_period_result_list(period_counts, period, date_to)
            return result
        result = ReadLog.create_summary_log_with_period_result_list(period_counts, period, date_to, end_date_in_file)
        result_index = 0
        pointer = 0
        while result_index < period_counts and pointer < len(self.data):
            line_data = self.data[pointer]
            line_date = self.get_date_in_line(line_data, extra_precision=True)
            if line_date:
                if line_date > result[result_index].time:
                    result_index += 1
                    if result_index < period_counts:
                        result[result_index].number_of_logs = result[result_index - 1].number_of_logs
                else:
                    log_type_inline = line_data[20:50]

                    if log_type == 'OTHER':

                        if not any(log_type in log_type_inline for log_type in ReadLog.log_type_list):
                            result[result_index].number_of_logs += 1

                    elif log_type == 'ALL':
                        result[result_index].number_of_logs += 1
                    else:
                        if log_type in log_type_inline:
                            result[result_index].number_of_logs += 1
                    pointer += 1
            else:
                pointer += 1
        return result

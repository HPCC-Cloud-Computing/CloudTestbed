# Create your views here.
from read_log_file import readfile
import datetime
from django.http import HttpResponse
import json
import time
import os.path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
log_types_list = {'info': 'INFO', 'debug': 'DEBUG', 'error': 'ERROR', 'warning': 'WARNING', 'other': 'OTHER',
                  'all': 'ALL'}


def index(request):
    pass


def nova_log_view(request):
    start_date_input = request.GET.get('date_from')
    end_date_input = request.GET.get('date_to')
    if (not check_is_valid_date(start_date_input) or not check_is_valid_date(end_date_input)) or \
            (not check_valid_date_from_and_date_to(start_date_input, end_date_input)):
        return HttpResponse(json.dumps({"result": "invalid input"}), status=404)
    log_reader = readfile.ReadLog(PROJECT_ROOT+"/n-api.log")
    log_summary_result = log_reader.summary_log_counts(start_date_input, end_date_input)
    return HttpResponse(json.dumps(log_summary_result.__dict__, ), status=200)


def nova_log_count_per_day_view(request):
    start_date_input = request.GET.get('date_from')
    end_date_input = request.GET.get('date_to')
    log_type = request.GET.get("log_type")
    if (not check_is_valid_date(start_date_input) or not check_is_valid_date(end_date_input)) or \
            (not check_valid_date_from_and_date_to(start_date_input, end_date_input)):
        return HttpResponse(json.dumps({'error': "invalid date value"}), status=404)
    if log_type not in log_types_list:
        return HttpResponse(json.dumps({'error': "invalid log_type value"}), status=404)
    log_reader = readfile.ReadLog(PROJECT_ROOT+"/n-api.log")
    try:
        result_dict = log_reader.summary_log_per_day(log_types_list[log_type],
                                                     start_date_input, end_date_input)
    except readfile.ReadLog.DateException:
        return HttpResponse(json.dumps([]), status=200)
    result_obj_array = [SortObj(key, value) for key, value in result_dict.iteritems()]
    result_obj_array.sort(key=lambda x: x.date, reverse=False)
    return HttpResponse(json.dumps([{x.date: x.value} for x in result_obj_array]), status=200)


class SortObj:
    def __init__(self, date, value):
        self.date = date
        self.value = value


def check_is_valid_date(string_date_check):
    if string_date_check == 'none':
        return True
    else:
        try:
            datetime.datetime.strptime(string_date_check, "%Y-%m-%d")
            return True
        except TypeError:
            return False
        except ValueError:
            return False


def check_valid_date_from_and_date_to(date_from, date_to):
    if date_from != 'none' and date_to != 'none':
        try:
            date_from_date_format = datetime.datetime.strptime(date_from, "%Y-%m-%d")
            date_to_date_format = datetime.datetime.strptime(date_to, "%Y-%m-%d")
            if date_to_date_format >= date_from_date_format:
                return True
            else:
                return False
        except ValueError:
            return False
    return True


class PeriodInputException(Exception):
    pass


def get_period_value(input_period_value):
    try:
        input_period = int(input_period_value)
    except ValueError:
        raise PeriodInputException("not a number")
    if input_period < 0 or input_period > 60:
        raise PeriodInputException("not in valid range")
    return input_period


def convert_datetime_to_result_string(date_input):
    return str(date_input.year) + '-' + str(date_input.month) + '-' + str(date_input.day) + 'T' + \
           str(date_input.hour) + ':' + str(date_input.minute) + ':' + str(date_input.second)


def nova_log_count_with_period_and_log_type(request):
    """
    Process request with request inputs is log_type, date_to and period

    @:parameter log_type: must be one of ("info", "debug", "other", "warning", "all")
    @:parameter date_to: string type, must be in format YY-mm-dd
    @:parameter period: string represent a int from 10 to 60

    return HTTP 400 if invalid input
    """
    log_type = request.GET.get("log_type")
    if log_type not in log_types_list:
        return HttpResponse(json.dumps({'error': "invalid log_type value"}), status=400)
    log_type = log_types_list[log_type]
    date_to = request.GET.get("date_to")
    if not check_is_valid_date(date_to):
        return HttpResponse(json.dumps({'error': "invalid date_to value"}), status=400)
    try:
        period = get_period_value(request.GET.get("period"))
    except PeriodInputException:
        return HttpResponse(json.dumps({'error': "invalid period value"}), status=400)
    log_reader = readfile.ReadLog(PROJECT_ROOT+"/n-api.log")
    result = log_reader.summary_log_with_period(date_to, log_type, period, period_counts=5)
    result_json_format = [{convert_datetime_to_result_string(elements.time): elements.number_of_logs} for elements in
                          result]
    return HttpResponse(json.dumps(result_json_format), status=200)


def realtime(request):
    """
    Process request with request inputs is log_type, date_to and period

    @:parameter log_type: must be one of ("info", "debug", "other", "warning", "all")
    @:parameter date_to: string type, must be in format YY-mm-dd
    @:parameter period: string represent a int from 10 to 60

    return HTTP 400 if invalid input
    """
    entries_number = request.GET.get("entries_number")
    print(entries_number)
    data_result = []
    for x in ["info", "debug", "error"]:
        k = 0
        data = []
        while k < 60:
            data.append({"sample" + str(k): k})
            k += 1
        data_result.append(ReatimeResult(x, data).__dict__)
    time.sleep(0.2)

    return HttpResponse(json.dumps(data_result), status=200)


class ReatimeResult:
    def __init__(self, label, data):
        self.label = label
        self.data = data

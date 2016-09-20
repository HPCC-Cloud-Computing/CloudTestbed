# Create your views here.
from django.shortcuts import render
from read_log_file import readfile
from datetime import datetime as date_maker
from datetime import timedelta
from django.http import HttpResponse
import json
from random import randint
import os.path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
import time


def convert_string_to_date(date_data):
    return date_maker(int(date_data[0:4]), int(date_data[5:7]), int(date_data[8:10]))


def index(request):
    return render(request, 'line_chart/index.html', dict())


# next plan, story history in database, write program eventually update database each 1 second,
#  and get data from database
# data type is one of 3 values : debug, error, info
class HistoryData:
    def __init__(self, time_stamp, value):
        self.time_stamp = time_stamp.strftime('%Y-%m-%d-%H-%M-%S')
        self.value = value

    # next plan, end_time is the last entries of history data in database
    @staticmethod
    def get_history_data_list(entries_number, data_type_list):
        history_data_list = []
        for data_type in data_type_list:
            history_data = {"data_type": data_type}
            data = []
            end_time = date_maker.now()+timedelta(hours=7)
            print(end_time)
            time_index = end_time - timedelta(seconds=entries_number-1)
            i = 0
            while time_index <= end_time:
                data.append(HistoryData(time_stamp=time_index, value=randint(50,150)).__dict__)
                time_index += timedelta(seconds=1)
                i += 2
            history_data['data_list'] = data
            history_data_list.append(history_data)
        return history_data_list


def realtime_history_data(request):
    """
    Process request with request inputs is log_type, date_to and period

    @:parameter log_type: must be one of ("info", "debug", "other", "warning", "all")
    @:parameter date_to: string type, must be in format YY-mm-dd
    @:parameter period: string represent a int from 10 to 60

    return HTTP 400 if invalid input
    """
    print(PROJECT_ROOT+"/test.log")
    entries_number = int(request.GET.get("entries_number"))
    request_selected_type_list = []
    if request.GET.get("data-warning") is not None:
        request_selected_type_list.append("data-warning")
    if request.GET.get("data-info") is not None:
        request_selected_type_list.append("data-info")
    if request.GET.get("data-error") is not None:
        request_selected_type_list.append("data-error")
    history_type_data = HistoryData.get_history_data_list(entries_number, data_type_list=request_selected_type_list)
    time.sleep(0.3)
    return HttpResponse(json.dumps(history_type_data), status=200)


class ReatimeHistoryData:
    def __init__(self, type, data):
        self.type = type
        self.data = data


def realtime_data(request):
    """
    Process request with request inputs is log_type, date_to and period

    @:parameter log_type: must be one of ("info", "debug", "other", "warning", "all")
    @:parameter date_to: string type, must be in format YY-mm-dd
    @:parameter period: string represent a int from 10 to 60

    return HTTP 400 if invalid input
    """
    is_debug_data = request.GET.get("warning")
    is_error_data = request.GET.get("error")
    is_info_data = request.GET.get("info")

    current_time = date_maker.now()
    current_time_str = current_time.strftime('%Y-%m-%d-%H-%M-%S')
    current_info_value = 50 + randint(0, 60)
    current_debug_value = 40 + randint(0, 40)
    current_error_value = 70 + randint(0, 80)
    data_result = []
    if is_debug_data:
        data_result.append(RealTimeData('debug', {'time': current_time_str, 'value': current_debug_value}).__dict__)
    if is_error_data:
        data_result.append(RealTimeData('error', {'time': current_time_str, 'value': current_error_value}).__dict__)
    if is_info_data:
        data_result.append(RealTimeData('info', {'time': current_time_str, 'value': current_info_value}).__dict__)

    return HttpResponse(json.dumps(data_result), status=200)


class RealTimeData:
    def __init__(self, data_name, data_value):
        self.data_name = data_name
        self.data_value = data_value

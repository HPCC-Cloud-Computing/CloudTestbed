import requests
import json
from requests.adapters import ConnectionError
import datetime

MAX_URI_LEN = 8192
USER_AGENT = 'python-neutron-sks'

ENDPOINT_URL = u'http://localhost:8080/api/'


#
# class LogSummary:
#     def __init__(self, info_number, warning_number, error_number, debug_number, other_number, total_number):
#         self.info_number = info_number
#         self.warning_number = warning_number
#         self.error_number = error_number
#         self.debug_number = debug_number
#         self.other_number = other_number
#         self.total_number = total_number


def request(url, method, body=None, headers=None, **kwargs):
    """Request without authentication."""

    content_type = kwargs.pop('content_type', None) or 'application/json'
    headers = headers or {}
    headers.setdefault('Accept', content_type)

    if body:
        headers.setdefault('Content-Type', content_type)

    headers['User-Agent'] = USER_AGENT
    try:
        resp = requests.request(
            method,
            url,
            data=body,
            headers=headers,
            # verify=self.verify_cert,
            # timeout=self.timeout,
            **kwargs)
    except:
        raise ConnectionError
    return resp, resp.text


def get_date_from_input(date_input):
    if date_input is None:
        return None
    elif not date_input:
        return "none"
    else:
        try:
            return datetime.datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            return None


class InputError(Exception):
    pass



def check_is_valid_date(string_date_check):
    if string_date_check == 'none':
        return True
    else:
        try:
            datetime.datetime.strptime(string_date_check, "%Y-%m-%d")
            return True
        except ValueError:
            return False


def get_all_container_data(date_from=None, date_to=None):
    # endpoint = None
    method = "GET"
    # if date_to != 'none':
    #     end_date = date_to.strftime('%Y-%m-%d')
    # else:
    #     end_date = date_to
    endpoint =  u'http://localhost:8080/api/'
    endpoint += "v1.2/docker/"
    # " + log_type + " & date_to = " + end_date + " & period = " + period
    try:
        resp, reply_body = request(endpoint, method, body={})
        status_code = resp.status_code
        if status_code in (requests.codes.ok,
                           requests.codes.created,
                           requests.codes.accepted,
                           requests.codes.no_content):
            data = json.loads(reply_body)
            return data
        else:
            return "Error"
    except ConnectionError:
        return "Error"

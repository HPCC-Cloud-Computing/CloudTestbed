import requests
import serializer
from six import string_types

MAX_URI_LEN = 8192
USER_AGENT = 'python-neutron-sks'


# CONTENT_TYPE = 'application/json'


def deserialize(data, status_code):
    """Deserializes a JSON string into a dictionary."""
    if status_code == 204:
        return data
    return serializer.Serializer().deserialize(
        data)['body']


class _RequestIdMixin(object):
    """Wrapper class to expose x-openstack-request-id to the caller."""

    def _request_ids_setup(self):
        self._request_ids = []

    @property
    def request_ids(self):
        return self._request_ids

    def _append_request_ids(self, resp):
        """Add request_ids as an attribute to the object

        :param resp: Response object or list of Response objects
        """
        if isinstance(resp, list):
            # Add list of request_ids if response is of type list.
            for resp_obj in resp:
                self._append_request_id(resp_obj)
        elif resp is not None:
            # Add request_ids if response contains single object.
            self._append_request_id(resp)

    def _append_request_id(self, resp):
        if isinstance(resp, requests.Response):
            # Extract 'x-openstack-request-id' from headers if
            # response is a Response object.
            request_id = resp.headers.get('x-openstack-request-id')
            # log request-id for each api call
            # _logger.debug('%(method)s call to neutron for '
            #               '%(url)s used request id '
            #               '%(response_request_id)s',
            #               {'method': resp.request.method,
            #                'url': resp.url,
            #                'response_request_id': request_id})
        else:
            # If resp is of type string.
            request_id = resp
        if request_id:
            self._request_ids.append(request_id)


def _convert_into_with_meta(item, resp):
    if item:
        if isinstance(item, dict):
            return _DictWithMeta(item, resp)
        elif isinstance(item, string_types):
            return _StrWithMeta(item, resp)
    else:
        return _TupleWithMeta((), resp)


class _DictWithMeta(dict, _RequestIdMixin):
    def __init__(self, values, resp):
        super(_DictWithMeta, self).__init__(values)
        self._request_ids_setup()
        self._append_request_ids(resp)


class _TupleWithMeta(tuple, _RequestIdMixin):
    def __new__(cls, values, resp):
        return super(_TupleWithMeta, cls).__new__(cls, values)

    def __init__(self, values, resp):
        self._request_ids_setup()
        self._append_request_ids(resp)


class _StrWithMeta(str, _RequestIdMixin):
    def __new__(cls, value, resp):
        return super(_StrWithMeta, cls).__new__(cls, value)

    def __init__(self, values, resp):
        self._request_ids_setup()
        self._append_request_ids(resp)


def request(url, method, body=None, headers=None, **kwargs):
    """Request without authentication."""

    content_type = kwargs.pop('content_type', None) or 'application/json'
    headers = headers or {}
    headers.setdefault('Accept', content_type)

    if body:
        headers.setdefault('Content-Type', content_type)

    headers['User-Agent'] = USER_AGENT

    resp = requests.request(
        method,
        url,
        data=body,
        headers=headers,
        # verify=self.verify_cert,
        # timeout=self.timeout,
        **kwargs)

    return resp, resp.text


def get_agent_list(keystone_token, endpoint):
    method = "GET"
    body = ''
    action = endpoint+"/v2.0/agents"
    header = {'X-Auth-Token': keystone_token}
    resp, replybody = request(action, method, body=body, headers=header)

    status_code = resp.status_code
    if status_code in (requests.codes.ok,
                       requests.codes.created,
                       requests.codes.accepted,
                       requests.codes.no_content):
        data = deserialize(replybody, status_code)
        return _convert_into_with_meta(data, resp)
    else:
        if not replybody:
            replybody = resp.reason

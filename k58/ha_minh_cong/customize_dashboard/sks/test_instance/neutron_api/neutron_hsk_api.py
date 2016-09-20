from __future__ import absolute_import
from openstack_dashboard.dashboards.sks.test_instance.neutron_api import neutronv2

from neutronclient.v2_0 import client as neutron_client
from keystoneclient.v2_0 import client



def get_token(request):
    keystone = client.Client(username='admin',
                             password='bkcloud',
                             tenant_name='admin',
                             auth_url=get_endpoint(request,'identity','admin')
                             )

    return keystone.auth_ref.auth_token

# pickle or whatever you like here
# new_client = client.Client(auth_ref=auth_ref)



class APIDictWrapper(object):
    """Simple wrapper for api dictionaries

    Some api calls return dictionaries.  This class provides identical
    behavior as APIResourceWrapper, except that it will also behave as a
    dictionary, in addition to attribute accesses.

    Attribute access is the preferred method of access, to be
    consistent with api resource objects from novaclient.
    """

    _apidict = {}  # Make sure _apidict is there even in __init__.

    def __init__(self, apidict):
        self._apidict = apidict

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if attr not in self._apidict:
                raise
            return self._apidict[attr]

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except (AttributeError, TypeError) as e:
            # caller is expecting a KeyError
            raise KeyError(e)

    def __contains__(self, item):
        try:
            return hasattr(self, item)
        except TypeError:
            return False

    def get(self, item, default=None):
        try:
            return getattr(self, item)
        except (AttributeError, TypeError):
            return default

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self._apidict)

    def to_dict(self):
        return self._apidict


class NeutronAPIDictWrapper(APIDictWrapper):
    def __init__(self, apidict):
        if 'admin_state_up' in apidict:
            if apidict['admin_state_up']:
                apidict['admin_state'] = 'UP'
            else:
                apidict['admin_state'] = 'DOWN'

        # Django cannot handle a key name with ':', so use '__'.
        apidict.update({
                           key.replace(':', '__'): value
                           for key, value in apidict.items()
                           if ':' in key
                           })
        super(NeutronAPIDictWrapper, self).__init__(apidict)


class Agent(NeutronAPIDictWrapper):
    """Wrapper for neutron agents."""
def get_endpoint(request, service_name,role):
    try:
        for service in request.user.service_catalog:
            if service['type']== service_name:
                for endpoint in service['endpoints']:
                    if role=='admin' and endpoint['interface'] =='admin':
                        return endpoint['url']
                    elif role=='user' and endpoint['interface']=='public':
                        return endpoint['url']
    except Exception :
        return None


def neutronclient(request):
    c = neutron_client.Client(
        # username='admin', password='bkcloud',
        token=request.user.token.id,
        auth_url=get_endpoint(request,service_name='identity',role='admin'),
        #endpoint_url=u'http://bkcloud12:9696',
        endpoint_url=get_endpoint(request,service_name='network',role='admin')
    )
    # token=request.user.token.id,
    # c = neutron_client.Client(username='admin', password='bkcloud',auth_url=u'http://bkcloud12:35357/v2.0',
    # endpoint_url = u'http://bkcloud12:9696',                        )
    return c


def agent_list(request, **params):
    # agents = neutronclient(request).list_agents()
    agents = neutronv2.get_agent_list(keystone_token=get_token(request),
                                 endpoint=get_endpoint(request, service_name='network', role='admin'))
    return [Agent(a) for a in agents['agents']]


# k = subnet_list(1)
# print(k)

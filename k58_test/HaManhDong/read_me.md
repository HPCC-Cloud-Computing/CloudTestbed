1. Cài đặt gói docker-py

2. Trong thư mục `openstack_dashboard/enabled` tạo file `__50_mydashboard.py` có nội dung:

```sh
# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'mydashboard'

# If set to True, this dashboard will not be added to the settings.
DISABLED = False

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'openstack_dashboard.dashboards.mydashboard',
]
```

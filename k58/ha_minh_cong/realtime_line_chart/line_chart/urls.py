from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^realtime_history_data/$', views.realtime_history_data, name='realtime_history'),
    url(r'^realtime_data/$', views.realtime_data, name='realtime_data'),
    url(r'^$', views.index, name='index'),

]

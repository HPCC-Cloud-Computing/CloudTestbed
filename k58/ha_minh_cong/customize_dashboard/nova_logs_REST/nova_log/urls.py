from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^$', views.index),
    url(r'^summary/$', views.nova_log_view),  # good
    url(r'^count_log_per_day/$', views.nova_log_count_per_day_view),  # good
    url(r'^count_log_with_period/$', views.nova_log_count_with_period_and_log_type),  # good
]

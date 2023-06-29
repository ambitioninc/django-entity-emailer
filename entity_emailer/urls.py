from django.urls import re_path

from entity_emailer.views import EmailView


urlpatterns = [
    re_path(r'^([0-9a-z\-]+)/$', EmailView.as_view(), name='entity_emailer.email'),
]

from django.conf.urls import url

from entity_emailer.views import EmailView


urlpatterns = [
    url(r'^([0-9a-z\-]+)/$', EmailView.as_view(), name='entity_emailer.email'),
]

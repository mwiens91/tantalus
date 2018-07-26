"""Contains URL routing for backend views."""

from django.conf.urls import url
from tantalus.backend.views import ReadModelsView

app_name='backend'
urlpatterns = [
    url(r'^read_models/$', ReadModelsView.as_view(), name='read_models'),
]

from django.urls import path

from hub.views import HubView

app_name = 'hub'

urlpatterns = [
    path('<slug:slug>', HubView.as_view(), name='hub'),
]

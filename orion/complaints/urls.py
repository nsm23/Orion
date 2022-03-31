from django.urls import path
from complaints.views import ComplaintCreateView


app_name = 'complaints'
urlpatterns = [
    path('save/', ComplaintCreateView.as_view(), name='save'),
]

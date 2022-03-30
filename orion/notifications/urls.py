from django.urls import path

from . import views


app_name = 'notifications'
urlpatterns = [
    path('header/', views.get_notifications, name='to_header'),
    path('mark-as-read/', views.mark_as_read, name='mark_as_read'),
    path('mark-as-read/<str:object_model>/<int:object_id>/', views.mark_as_read_and_redirect,
         name='mark_as_read_and_redirect'),
]

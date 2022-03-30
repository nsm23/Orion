from django.urls import path
from .views import CommentCreateView


app_name = 'comments'
urlpatterns = [
    path('save/', CommentCreateView.as_view(), name='save'),
]

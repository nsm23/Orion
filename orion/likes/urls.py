from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from .models import LikeDislike
from posts.models import Post

app_name = 'likes'

urlpatterns = [
    path('posts/<int:pk>/like/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE)),
         name='post_like'),
    path('posts/<int:pk>/dislike/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE)),
         name='post_dislike'),

]

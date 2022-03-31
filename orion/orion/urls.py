from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from hub.views import MainView

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('tinymce/', include('tinymce.urls')),
    path('hub/', include('hub.urls', namespace='hubs')),
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls', namespace='posts')),
    path('comments/', include('comments.urls', namespace='comments')),
    path('complaints/', include('complaints.urls', namespace='complaints')),
    path('cabinet/', include('users.urls', namespace='cabinet')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('moderation/', include('moderation.urls', namespace='moderation')),
    path('', include('likes.urls', namespace='likes')),
    path('', include('social_django.urls', namespace='social')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root='static/')

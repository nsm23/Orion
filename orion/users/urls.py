from django.urls import path

from users import views

app_name = 'users'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('status/<int:pk>/<slug:status>', views.set_status, name='set_status'),
    path('<int:pk>/', views.UserProfileView.as_view(), name='user_detail'),
    path('<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('<int:pk>/<str:section>/', views.UserProfileView.as_view(), name='user_profile'),
]

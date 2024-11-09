from django.urls import path
from . import views

urlpatterns = [
    path('user/login/', views.User_login_view, name='user_login'),
    path('user/register/', views.register_view, name='user_register'),
    path('user/logout/', views.logout_view, name='user_logout'),
    path('manager/', views.manager_login, name='manager_login'),
] 
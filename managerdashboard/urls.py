# managerdashboard/urls.py



from django.urls import path



from . import views



app_name = 'managerdashboard'



urlpatterns = [

    path('', views.manager_dashboard, name='manager_dashboard'),

    path('reports/', views.reports, name='reports'),

    path('orders/', views.orders, name='orders'),

    path('services/', views.services, name='services'),

    path('tickets/', views.tickets, name='tickets'),

    path('users/', views.users, name='users'),

    path('subscribers/', views.subscribers, name='subscribers'),

    path('providers/', views.providers, name='providers'),

    path('payments/', views.payments, name='payments'),

    path('settings/', views.settings, name='settings'),

    path('users/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    path('users/add/', views.add_user, name='add_user'),

]















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

    path('users/<int:user_id>/get-info/', views.get_user_info, name='get_user_info'),

    path('users/edit/', views.edit_user, name='edit_user'),

    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    path('users/add-funds/', views.add_funds, name='add_funds'),

    path('users/set-password/', views.set_password, name='set_password'),

    path('users/send-mail/', views.send_mail, name='send_mail'),

]















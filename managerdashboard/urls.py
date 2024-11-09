# managerdashboard/urls.py



from django.urls import path



from . import views



app_name = 'managerdashboard'



urlpatterns = [

    path('', views.manager_dashboard, name='manager_dashboard'),

    path('orders/', views.orders, name='orders'),

    path('services/', views.services, name='services'),

    path('tickets/', views.tickets, name='tickets'),

    path('tickets/<int:ticket_id>/view/', views.view_ticket, name='view_ticket'),

    path('tickets/<int:ticket_id>/reply/', views.reply_ticket, name='reply_ticket'),

    path('tickets/<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),

    path('tickets/add/', views.add_ticket, name='add_ticket'),

    path('users/', views.users, name='users'),

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

    path('providers/add/', views.add_provider, name='add_provider'),

    path('providers/<int:provider_id>/toggle-status/', views.toggle_provider_status, name='toggle_provider_status'),

    path('providers/add-funds/', views.add_provider_funds, name='add_provider_funds'),

    path('providers/<int:provider_id>/get-info/', views.get_provider_info, name='get_provider_info'),

    path('providers/<int:provider_id>/check-balance/', views.check_provider_balance, name='check_provider_balance'),

    path('providers/<int:provider_id>/sync-services/', views.sync_provider_services, name='sync_provider_services'),

    path('providers/<int:provider_id>/services/', views.provider_services, name='provider_services'),

    path('providers/<int:provider_id>/delete/', views.delete_provider, name='delete_provider'),

    path('providers/<int:provider_id>/edit/', views.edit_provider, name='edit_provider'),

    path('providers/import-services/', views.import_services, name='import_services'),

]















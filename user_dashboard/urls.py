from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='user_dashboard'),
    path('profile/', views.profile, name='user_profile'),
    path('profile/more/', views.profile_more, name='user_profile_more'),
    path('profile/generate-api-key/', views.generate_api_key, name='generate_api_key'),
    path('security/', views.security_settings, name='security_settings'),
    path('posts/', views.posts, name='user_posts'),
    path('favorites/', views.favorites, name='user_favorites'),
    path('messages/', views.user_messages, name='user_messages'),
    path('notifications/', views.notifications, name='user_notifications'),
    path('preferences/', views.preferences, name='user_preferences'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('new-order/', views.new_order, name='new_order'),
    path('order-log/', views.order_log, name='order_log'),
    path('services/', views.services, name='services'),
    path('api-docs/', views.api_documentation, name='api_documentation'),
    path('add-funds/', views.add_funds, name='add_funds'),
    path('transaction-logs/', views.transaction_logs, name='transaction_logs'),
    path('process-payment/<int:method_id>/', views.process_payment, name='process_payment'),
]
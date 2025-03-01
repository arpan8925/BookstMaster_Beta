from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Count, Sum
from authentication.models import User
from user_dashboard.models import Ticket, TicketMessage  
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail as django_send_mail
from django.conf import settings
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.views.decorators.http import require_POST
from .models import (
    Provider, 
    ProviderTransaction,
    Service,
    ServiceCategory,
    ServiceUpdate,
    PaymentMethod,
    Transactions
)

import requests
from django.utils import timezone

import json

import logging
logger = logging.getLogger(__name__)



@permission_required('authentication.is_manager', login_url='manager_login')
def manager_dashboard(request):
    # Get statistics
    total_users = User.objects.count()
    total_tickets = Ticket.objects.count()
    total_orders = 197  # Replace with actual order count
    total_revenue = 340282346638528  # Replace with actual revenue calculation    

    context = {

        'active_tab': 'dashboard',

        'total_users': total_users,

        'total_tickets': total_tickets,

        'total_orders': total_orders,

        'total_revenue': total_revenue,

    }

    return render(request, 'managerdashboard/dashboard.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def orders(request):
    # Get search query and filters

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', 'today')    

    # Base queryset with related user and service

    orders = Order.objects.select_related('user', 'service').all()

    

    # Apply search filter

    if search_query:

        orders = orders.filter(

            Q(id__icontains=search_query) |

            Q(user__email__icontains=search_query) |

            Q(link__icontains=search_query)

        )

    

    # Apply status filter

    if status_filter:

        orders = orders.filter(status=status_filter)

    

    # Apply date filter

    today = timezone.now().date()

    if date_filter == 'today':

        orders = orders.filter(created__date=today)

    elif date_filter == 'yesterday':

        yesterday = today - timedelta(days=1)

        orders = orders.filter(created__date=yesterday)

    elif date_filter == 'last7days':

        last_week = today - timedelta(days=7)

        orders = orders.filter(created__date__gte=last_week)

    elif date_filter == 'last30days':

        last_month = today - timedelta(days=30)

        orders = orders.filter(created__date__gte=last_month)

    

    # Get counts for stats

    total_orders = orders.count()

    pending_orders = orders.filter(status='pending').count()

    processing_orders = orders.filter(status='processing').count()

    completed_orders = orders.filter(status='completed').count()

    

    # Pagination

    paginator = Paginator(orders, 25)  # Show 25 orders per page

    page_number = request.GET.get('page')

    orders_page = paginator.get_page(page_number)

    

    context = {

        'active_tab': 'orders',

        'orders': orders_page,

        'total_orders': total_orders,

        'pending_orders': pending_orders,

        'processing_orders': processing_orders,

        'completed_orders': completed_orders,

        'search_query': search_query,

        'status_filter': status_filter,

        'date_filter': date_filter

    }

    return render(request, 'managerdashboard/orders.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def services(request):
    # Get search query and filters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    provider_filter = request.GET.get('provider', '')
    status_filter = request.GET.get('status', '')

    

    # Base queryset

    services = Service.objects.select_related('provider', 'category')

    

    # Apply filters

    if search_query:

        services = services.filter(

            Q(name__icontains=search_query) |

            Q(service_id__icontains=search_query) |

            Q(provider__name__icontains=search_query)

        )

    

    if category_filter:

        services = services.filter(category__name=category_filter)

    

    if provider_filter:

        services = services.filter(provider_id=provider_filter)

    

    if status_filter:

        services = services.filter(status=status_filter)

    

    # Get unique categories and providers for filters

    categories = ServiceCategory.objects.filter(is_active=True)

    providers = Provider.objects.filter(is_active=True)

    

    # Pagination

    paginator = Paginator(services, 25)  # Show 25 services per page

    page_number = request.GET.get('page')

    services_page = paginator.get_page(page_number)

    

    context = {

        'active_tab': 'services',

        'services': services_page,

        'categories': categories,

        'providers': providers,

        'search_query': search_query,

        'category_filter': category_filter,

        'provider_filter': provider_filter,

        'status_filter': status_filter

    }

    return render(request, 'managerdashboard/services.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def tickets(request):

    # Get search query and filters

    search_query = request.GET.get('search', '')

    status_filter = request.GET.get('status', '')

    priority_filter = request.GET.get('priority', '')

    

    # Base queryset

    tickets = Ticket.objects.all().order_by('-created')

    

    # Get all active users for the add ticket modal

    all_users = User.objects.filter(is_active=True).order_by('email')

    

    # Apply filters

    if search_query:

        tickets = tickets.filter(

            Q(subject__icontains=search_query) |

            Q(user__email__icontains=search_query)

        )

    

    if status_filter:

        tickets = tickets.filter(status=status_filter)

    

    if priority_filter:

        tickets = tickets.filter(priority=priority_filter)

    

    # Count statistics

    total_tickets = tickets.count()

    pending_tickets = tickets.filter(status='pending').count()

    in_progress_tickets = tickets.filter(status='in_progress').count()

    completed_tickets = tickets.filter(status='completed').count()

    

    # Pagination

    paginator = Paginator(tickets, 10)  # Show 10 tickets per page

    page_number = request.GET.get('page')

    tickets_page = paginator.get_page(page_number)

    

    context = {

        'active_tab': 'tickets',

        'tickets': tickets_page,

        'total_tickets': total_tickets,

        'pending_tickets': pending_tickets,

        'in_progress_tickets': in_progress_tickets,

        'completed_tickets': completed_tickets,

        'search_query': search_query,

        'status_filter': status_filter,

        'priority_filter': priority_filter,

        'all_users': all_users,

    }

    return render(request, 'managerdashboard/tickets.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def users(request):

    # Get search query

    search_query = request.GET.get('search', '')

    status_filter = request.GET.get('status', '')

    

    # Base queryset

    users = User.objects.all().order_by('-date_joined')

    

    # Apply filters

    if search_query:

        users = users.filter(

            Q(email__icontains=search_query) |

            Q(username__icontains=search_query)

        )

    

    if status_filter:

        if status_filter == 'active':

            users = users.filter(is_active=True)

        elif status_filter == 'inactive':

            users = users.filter(is_active=False)

    

    # Count totals

    total_users = users.count()

    active_users = users.filter(is_active=True).count()

    inactive_users = users.filter(is_active=False).count()

    

    # Pagination

    paginator = Paginator(users, 10)  # Show 10 users per page

    page_number = request.GET.get('page')

    users_page = paginator.get_page(page_number)

    

    context = {

        'active_tab': 'users',

        'users': users_page,

        'total_users': total_users,

        'active_users': active_users,

        'inactive_users': inactive_users,

        'search_query': search_query,

        'status_filter': status_filter

    }

    return render(request, 'managerdashboard/users.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def toggle_user_status(request, user_id):

    if request.method != 'POST':

        return JsonResponse({'error': 'Invalid request method'}, status=405)

        

    try:

        user = User.objects.get(id=user_id)

        user.is_active = not user.is_active

        user.save()

        return JsonResponse({'status': 'success', 'is_active': user.is_active})

    except User.DoesNotExist:

        return JsonResponse({'error': 'User not found'}, status=404)



@permission_required('authentication.is_manager', login_url='manager_login')

def providers(request):

    # Get search query and filters

    search_query = request.GET.get('search', '')

    status_filter = request.GET.get('status', '')

    sort_by = request.GET.get('sort', 'name')

    

    # Base queryset

    providers_qs = Provider.objects.all()

    

    # Apply filters

    if search_query:

        providers_qs = providers_qs.filter(

            Q(name__icontains=search_query) |

            Q(description__icontains=search_query)

        )

    

    if status_filter == 'active':

        providers_qs = providers_qs.filter(is_active=True)

    elif status_filter == 'inactive':

        providers_qs = providers_qs.filter(is_active=False)

    

    # Apply sorting

    if sort_by == 'balance':

        providers_qs = providers_qs.order_by('-balance')

    elif sort_by == 'status':

        providers_qs = providers_qs.order_by('-is_active', 'name')

    else:  # default to name

        providers_qs = providers_qs.order_by('name')

    

    # Get counts for filter badges

    total_count = Provider.objects.count()

    active_count = Provider.objects.filter(is_active=True).count()

    inactive_count = Provider.objects.filter(is_active=False).count()

    

    # Pagination

    paginator = Paginator(providers_qs, 10)  # Show 10 providers per page

    page_number = request.GET.get('page')

    providers = paginator.get_page(page_number)

    

    context = {

        'active_tab': 'providers',

        'providers': providers,

        'total_count': total_count,

        'active_count': active_count,

        'inactive_count': inactive_count,

        'search_query': search_query,

        'status_filter': status_filter,

        'sort_by': sort_by

    }

    return render(request, 'managerdashboard/providers.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def add_provider(request):

    if request.method == 'POST':

        try:

            # Get form data

            name = request.POST.get('name')

            api_url = request.POST.get('api_url')

            api_key = request.POST.get('api_key')

            description = request.POST.get('description')

            is_active = request.POST.get('is_active') == 'on'

            

            # Validate required fields

            if not all([name, api_url, api_key]):

                return JsonResponse({

                    'error': 'Name, API URL, and API Key are required'

                }, status=400)

            

            # Create provider

            provider = Provider.objects.create(

                name=name,

                api_url=api_url,

                api_key=api_key,

                description=description,

                is_active=is_active

            )

            

            # Return success response

            return JsonResponse({

                'status': 'success',

                'message': f'Provider {name} created successfully',

                'provider_id': provider.id

            })

            

        except Exception as e:

            print(f"Error creating provider: {str(e)}")

            return JsonResponse({

                'error': f'Error creating provider: {str(e)}'

            }, status=400)

    

    return JsonResponse({

        'error': 'Invalid request method'

    }, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')

def toggle_provider_status(request, provider_id):

    if request.method == 'POST':

        try:

            provider = Provider.objects.get(id=provider_id)

            provider.is_active = not provider.is_active

            provider.save()

            return JsonResponse({

                'status': 'success',

                'is_active': provider.is_active

            })

        except Provider.DoesNotExist:

            return JsonResponse({'error': 'Provider not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')

def add_provider_funds(request):

    if request.method == 'POST':

        try:

            provider_id = request.POST.get('provider_id')

            amount = Decimal(request.POST.get('amount'))

            notes = request.POST.get('notes', '')

            

            if amount <= 0:

                return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

            

            with transaction.atomic():

                provider = Provider.objects.get(id=provider_id)

                provider.balance += amount

                provider.save()

                

                ProviderTransaction.objects.create(

                    provider=provider,

                    amount=amount,

                    type='credit',

                    notes=notes,

                    added_by=request.user

                )

                

            return JsonResponse({

                'status': 'success',

                'message': f'${amount} added to {provider.name}',

                'new_balance': str(provider.balance)

            })

        except Provider.DoesNotExist:

            return JsonResponse({'error': 'Provider not found'}, status=404)

        except Exception as e:

            return JsonResponse({'error': str(e)}, status=400)

            

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')

def payments(request):

    from datetime import datetime, timedelta
    
    # Get search query and filters
    search_query = request.GET.get('search', '')
    search_type = request.GET.get('type', 'transaction_id')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', 'all')
    
    # Base queryset with related user info
    transactions = Transactions.objects.select_related('user').all()
    
    # Apply search based on type
    if search_query:
        if search_type == 'transaction_id':
            transactions = transactions.filter(transaction_id__icontains=search_query)
        elif search_type == 'user':
            transactions = transactions.filter(
                Q(user__email__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )
        elif search_type == 'payment_id':
            transactions = transactions.filter(payment_method__icontains=search_query)
    
    # Apply status filter
    if status_filter:
        if status_filter == 'paid':
            transactions = transactions.filter(status='completed')
        elif status_filter == 'waiting':
            transactions = transactions.filter(status='waiting')
        elif status_filter == 'cancelled':
            transactions = transactions.filter(status='cancelled')
    
    # Apply date filter
    today = timezone.now().date()
    if date_filter == 'today':
        transactions = transactions.filter(created__date=today)
    elif date_filter == 'yesterday':
        yesterday = today - timedelta(days=1)
        transactions = transactions.filter(created__date=yesterday)
    elif date_filter == 'last7days':
        last_week = today - timedelta(days=7)
        transactions = transactions.filter(created__date__gte=last_week)
    elif date_filter == 'last30days':
        last_month = today - timedelta(days=30)
        transactions = transactions.filter(created__date__gte=last_month)
    elif date_filter == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                # Add one day to end_date to include the entire day
                end_date = end_date + timedelta(days=1)
                transactions = transactions.filter(created__date__range=[start_date, end_date])
            except ValueError:
                pass
    
    # Order by created date
    transactions = transactions.order_by('-created')
    
    # Calculate statistics
    total_count = transactions.count()
    total_amount = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    paid_count = transactions.filter(status='completed').count()
    waiting_count = transactions.filter(status='waiting').count()
    cancelled_count = transactions.filter(status='cancelled').count()
    
    context = {
        'active_tab': 'payments',
        'transactions': transactions,
        'total_count': total_count,
        'total_amount': total_amount,
        'paid_count': paid_count,
        'waiting_count': waiting_count,
        'cancelled_count': cancelled_count,
        'search_query': search_query,
        'search_type': search_type,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', '')
    }
    return render(request, 'managerdashboard/payments.html', context)



@permission_required('authentication.is_manager', login_url='manager_login') #Using this already
def approve_transaction(request, transaction_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                txn = Transactions.objects.select_for_update().get(id=transaction_id)                
                if txn.status != 'waiting':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Transaction cannot be approved'
                    }, status=400)                
                # Update transaction status
                txn.status = 'completed'
                txn.save()                
                # Add amount to user's balance
                user = txn.uid
                user.balance = user.balance + txn.amount
                user.save()                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Transaction approved successfully'
                })
                
        except Transactions.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Transaction not found'
            }, status=404)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)            

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')

def cancel_transaction(request, transaction_id):

    if request.method == 'POST':

        try:

            transaction = Transactions.objects.get(id=transaction_id)

            

            # Only allow cancelling waiting transactions

            if transaction.status != 'waiting':

                return JsonResponse({

                    'error': 'Only waiting transactions can be cancelled'

                }, status=400)

            

            # Update transaction status

            transaction.status = 'cancelled'

            transaction.save()

            

            return JsonResponse({

                'status': 'success',

                'message': 'Transaction cancelled successfully'

            })

            

        except Transactions.DoesNotExist:

            return JsonResponse({'error': 'Transaction not found'}, status=404)

        except Exception as e:

            return JsonResponse({'error': str(e)}, status=400)

            

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')

def settings(request):

    payment_methods = PaymentMethod.objects.all()

    context = {

        'active_tab': 'settings',

        'payment_methods': payment_methods

    }

    return render(request, 'managerdashboard/settings.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('managerdashboard:users')
            
        # Validate if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('managerdashboard:users')
        
        try:
            # Create new user
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                is_active=is_active
            )
            messages.success(request, f'User {username} created successfully')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            
        return redirect('managerdashboard:users')
        
    return redirect('managerdashboard:users')



@permission_required('authentication.is_manager', login_url='manager_login')
def get_user_info(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
            'balance': '0.00',  # Add actual balance logic
            'total_orders': 0,  # Add actual orders count
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)



@permission_required('authentication.is_manager', login_url='manager_login')
def edit_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()
            messages.success(request, f'User {user.username} updated successfully')
            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            username = user.username
            user.delete()
            return JsonResponse({'message': f'User {username} deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')
def add_funds(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount')
        notes = request.POST.get('notes', '')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

            with transaction.atomic():
                user = User.objects.get(id=user_id)
                user.balance = user.balance + amount
                user.save()

                # Create transaction record
                Transactions.objects.create(
                    user=user,
                    amount=amount,
                    type='credit',
                    notes=notes,
                    added_by=request.user
                )

            return JsonResponse({
                'status': 'success',
                'message': f'${amount} added to {user.username}\'s account',
                'new_balance': str(user.balance)
            })

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except (ValueError, InvalidOperation):
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@permission_required('authentication.is_manager', login_url='manager_login')
def set_password(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password')
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            
            if request.POST.get('send_email_notification') == 'on':
                # Send email notification
                django_send_mail(
                    'Password Updated',
                    f'Your password has been updated by the administrator.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            
            messages.success(request, f'Password updated for {user.username}')
        except User.DoesNotExist:
            messages.error(request, 'User not found')
    return redirect('managerdashboard:users')



@permission_required('authentication.is_manager', login_url='manager_login')
def send_mail(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        try:
            user = User.objects.get(id=user_id)
            django_send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            messages.success(request, f'Email sent to {user.username}')
        except User.DoesNotExist:
            messages.error(request, 'User not found')
    return redirect('managerdashboard:users')



@permission_required('authentication.is_manager', login_url='manager_login')
def view_ticket(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        deletion_date = ticket.scheduled_deletion
        
        data = {
            'id': ticket.id,
            'subject': ticket.subject,
            'content': ticket.description,
            'user_email': ticket.user.email,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': ticket.changed.strftime('%Y-%m-%d %H:%M:%S') if ticket.changed else None,
            'scheduled_deletion': deletion_date.strftime('%Y-%m-%d %H:%M:%S') if deletion_date else None
        }
        return JsonResponse(data)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)

@permission_required('authentication.is_manager', login_url='manager_login')
def reply_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            reply_content = request.POST.get('reply')
            
            # Add your reply logic here
            # For example, create a TicketReply model instance
            
            ticket.status = 'in_progress'
            ticket.save()
            
            return JsonResponse({'status': 'success'})
        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def close_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.status = 'closed'
            ticket.save()
            return JsonResponse({'status': 'success'})
        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def add_ticket(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            subject = request.POST.get('subject')
            content = request.POST.get('content')
            priority = request.POST.get('priority', 'medium')
            
            if not all([user_id, subject, content]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            user = User.objects.get(id=user_id)
            
            ticket = Ticket.objects.create(
                user=user,
                subject=subject,
                description=content,
                priority=priority,
                status='pending'
            )
            
            # Create initial message
            TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=content
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Ticket created successfully',
                'ticket_id': ticket.id
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'Selected user not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def get_provider_info(request, provider_id):
    try:
        provider = Provider.objects.get(id=provider_id)
        data = {
            'name': provider.name,
            'api_url': provider.api_url,
            'api_key': provider.api_key,
            'description': provider.description,
            'is_active': provider.is_active,
        }
        return JsonResponse(data)
    except Provider.DoesNotExist:
        return JsonResponse({'error': 'Provider not found'}, status=404)

@permission_required('authentication.is_manager', login_url='manager_login')
def check_provider_balance(request, provider_id):
    if request.method == 'POST':
        try:
            provider = Provider.objects.get(id=provider_id)
            
            # Make API request to check balance
            params = {
                'key': provider.api_key,
                'action': 'balance'
            }
            
            try:
                response = requests.post(provider.api_url, data=params, timeout=10)  # Add timeout
                response.raise_for_status()  # Raise exception for bad status codes
                data = response.json()
                
                if 'balance' in data:
                    # Update provider's balance in database
                    provider.balance = data['balance']
                    provider.save()
                    
                    return JsonResponse({
                        'status': 'success',
                        'balance': data['balance']
                    })
                else:
                    return JsonResponse({
                        'error': 'Invalid response from provider API'
                    }, status=400)
                    
            except requests.Timeout:
                return JsonResponse({
                    'error': 'Request timed out. Please try again.'
                }, status=408)
            except requests.RequestException as e:
                return JsonResponse({
                    'error': f'API request failed: {str(e)}'
                }, status=400)
                
        except Provider.DoesNotExist:
            return JsonResponse({'error': 'Provider not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def sync_provider_services(request, provider_id):
    if request.method == 'POST':
        try:
            provider = Provider.objects.get(id=provider_id)
            
            # Make API request to get services
            params = {
                'key': provider.api_key,
                'action': 'services'
            }
            
            response = requests.post(provider.api_url, data=params)
            services = response.json()
            
            if isinstance(services, list):
                # Update provider's last sync time
                provider.last_sync = timezone.now()
                provider.save()
                
                # Process services
                added = 0
                updated = 0
                removed = 0
                
                # Add logic here to sync services with your database
                # This is just a placeholder for the actual implementation
                
                return JsonResponse({
                    'status': 'success',
                    'added': added,
                    'updated': updated,
                    'removed': removed
                })
            else:
                return JsonResponse({
                    'error': 'Invalid response from provider'
                }, status=400)
                
        except Provider.DoesNotExist:
            return JsonResponse({'error': 'Provider not found'}, status=404)
        except requests.RequestException as e:
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def provider_services(request, provider_id):
    try:
        provider = Provider.objects.get(id=provider_id)
        
        # Make API request to get services
        params = {
            'key': provider.api_key,
            'action': 'services'
        }
        
        response = requests.post(provider.api_url, data=params)
        services = response.json()
        
        # Get unique categories
        categories = set()
        if isinstance(services, list):
            for service in services:
                if 'category' in service:
                    categories.add(service['category'])
        
        context = {
            'active_tab': 'providers',
            'provider': provider,
            'services': services,
            'categories': sorted(list(categories))
        }
        return render(request, 'managerdashboard/provider_services.html', context)
        
    except Provider.DoesNotExist:
        messages.error(request, 'Provider not found')
        return redirect('managerdashboard:providers')
    except requests.RequestException as e:
        messages.error(request, f'API request failed: {str(e)}')
        return redirect('managerdashboard:providers')

@permission_required('authentication.is_manager', login_url='manager_login')
def delete_provider(request, provider_id):
    if request.method == 'POST':
        try:
            provider = Provider.objects.get(id=provider_id)
            provider_name = provider.name
            provider.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'Provider {provider_name} deleted successfully'
            })
        except Provider.DoesNotExist:
            return JsonResponse({'error': 'Provider not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def edit_provider(request, provider_id):
    if request.method == 'POST':
        try:
            provider = Provider.objects.get(id=provider_id)
            
            # Update provider fields
            provider.name = request.POST.get('name')
            provider.api_url = request.POST.get('api_url')
            provider.api_key = request.POST.get('api_key')
            provider.description = request.POST.get('description')
            provider.is_active = request.POST.get('is_active') == 'on'
            
            # Validate required fields
            if not all([provider.name, provider.api_url, provider.api_key]):
                return JsonResponse({
                    'error': 'Name, API URL, and API Key are required'
                }, status=400)
            
            # Save changes
            provider.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Provider {provider.name} updated successfully'
            })
            
        except Provider.DoesNotExist:
            return JsonResponse({'error': 'Provider not found'}, status=404)
        except Exception as e:
            print(f"Error updating provider: {str(e)}")
            return JsonResponse({
                'error': f'Error updating provider: {str(e)}'
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def import_services(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            provider_id = data.get('provider_id')
            service_ids = data.get('service_ids', [])
            
            if not provider_id or not service_ids:
                return JsonResponse({
                    'error': 'Provider ID and service IDs are required'
                }, status=400)
            
            provider = Provider.objects.get(id=provider_id)
            
            # Make API request to get service details
            params = {
                'key': provider.api_key,
                'action': 'services'
            }
            
            response = requests.post(provider.api_url, data=params)
            all_services = response.json()
            
            # Filter selected services
            selected_services = [s for s in all_services if str(s.get('service')) in service_ids]
            
            # Import services logic here
            imported = 0
            for service in selected_services:
                # Add your service import logic here
                imported += 1
            
            return JsonResponse({
                'status': 'success',
                'imported': imported,
                'message': f'Successfully imported {imported} services'
            })
            
        except Provider.DoesNotExist:
            return JsonResponse({'error': 'Provider not found'}, status=404)
        except requests.RequestException as e:
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def add_service(request):
    if request.method == 'POST':
        try:
            print("Received POST request for add_service")
            print("POST data:", request.POST)
            
            # Get or create category
            category, _ = ServiceCategory.objects.get_or_create(
                name=request.POST.get('category'),
                defaults={'is_active': True}
            )
            print("Category:", category)
            
            # Set the provider statically as "Official Provider"
            provider, _ = Provider.objects.get_or_create(
                name="Official Provider",
                defaults={
                    'api_url': "https://officialprovider.com",
                    'api_key': "official_key",
                    'is_active': True
                }
            )
            print("Provider:", provider)
            
            # Create service
            service = Service.objects.create(
                service_id=f'SRV{int(timezone.now().timestamp())}',
                name=request.POST.get('name'),
                provider=provider,  # Set the provider here
                category=category,
                rate=Decimal(request.POST.get('rate')),
                min_order=int(request.POST.get('min_order')),
                max_order=int(request.POST.get('max_order')),
                description=request.POST.get('description', ''),
                status='active' if request.POST.get('is_active') == 'on' else 'inactive',
                is_drip_feed=request.POST.get('is_drip_feed') == 'on'
            )
            print("Service created:", service)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Service created successfully',
                'service_id': service.id
            })
            
        except Exception as e:
            print(f"Error in add_service: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    print("Invalid request method for add_service")
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def edit_service(request, service_id):
    if request.method == 'POST':
        try:
            service = Service.objects.get(id=service_id)
            
            # Get the category instance (don't create if doesn't exist)
            try:
                category = ServiceCategory.objects.get(name=request.POST.get('category'))
            except ServiceCategory.DoesNotExist:
                return JsonResponse({
                    'error': f'Category "{request.POST.get("category")}" does not exist'
                }, status=400)
            
            # Create update record
            ServiceUpdate.objects.create(
                service=service,
                old_rate=service.rate,
                new_rate=request.POST.get('rate'),
                old_min=service.min_order,
                new_min=request.POST.get('min_order'),
                old_max=service.max_order,
                new_max=request.POST.get('max_order'),
                old_status=service.status,
                new_status='active' if request.POST.get('is_active') == 'on' else 'inactive',
                updated_by=request.user
            )
            
            # Update service
            service.name = request.POST.get('name')
            service.category = category  # Assign the category instance
            service.rate = request.POST.get('rate')
            service.min_order = request.POST.get('min_order')
            service.max_order = request.POST.get('max_order')
            service.description = request.POST.get('description')
            service.status = 'active' if request.POST.get('is_active') == 'on' else 'inactive'
            service.is_drip_feed = request.POST.get('is_drip_feed') == 'on'
            service.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Service updated successfully'
            })
            
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def toggle_service_status(request, service_id):
    if request.method == 'POST':
        try:
            service = Service.objects.get(id=service_id)
            service.status = 'inactive' if service.status == 'active' else 'active'
            service.save()
            
            return JsonResponse({
                'status': 'success',
                'is_active': service.status == 'active'
            })
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def delete_service(request, service_id):
    if request.method == 'POST':
        try:
            service = Service.objects.get(id=service_id)
            service.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Service deleted successfully'
            })
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def categories(request):
    # Get search query and filters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    categories = ServiceCategory.objects.all()
    
    # Apply filters
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter == 'active':
        categories = categories.filter(is_active=True)
    elif status_filter == 'inactive':
        categories = categories.filter(is_active=False)
    
    # Add service count to each category using the correct related name
    categories = categories.annotate(service_count=Count('services'))
    
    context = {
        'active_tab': 'categories',
        'categories': categories,
        'search_query': search_query,
        'status_filter': status_filter
    }
    return render(request, 'managerdashboard/categories.html', context)

@permission_required('authentication.is_manager', login_url='manager_login')
def add_category(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == 'on'
            
            # Validate name is unique
            if ServiceCategory.objects.filter(name=name).exists():
                return JsonResponse({
                    'error': 'Category with this name already exists'
                }, status=400)
            
            # Create category
            category = ServiceCategory.objects.create(
                name=name,
                description=description,
                is_active=is_active
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Category {name} created successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def edit_category(request, category_id):
    if request.method == 'POST':
        try:
            category = ServiceCategory.objects.get(id=category_id)
            
            # Check if new name conflicts with existing category
            new_name = request.POST.get('name')
            if new_name != category.name and ServiceCategory.objects.filter(name=new_name).exists():
                return JsonResponse({
                    'error': 'Category with this name already exists'
                }, status=400)
            
            # Store old name to update related services
            old_name = category.name
            
            # Update category
            category.name = new_name
            category.description = request.POST.get('description')
            category.is_active = request.POST.get('is_active') == 'on'
            category.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Category {category.name} updated successfully'
            })
            
        except ServiceCategory.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def toggle_category_status(request, category_id):
    if request.method == 'POST':
        try:
            category = ServiceCategory.objects.get(id=category_id)
            category.is_active = not category.is_active
            category.save()
            
            return JsonResponse({
                'status': 'success',
                'is_active': category.is_active
            })
        except ServiceCategory.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def delete_category(request, category_id):
    if request.method == 'POST':
        try:
            category = ServiceCategory.objects.get(id=category_id)
            
            # Check if category has services
            if category.services.exists():
                return JsonResponse({
                    'error': 'Cannot delete category that has services. Please reassign or delete the services first.'
                }, status=400)
            
            category_name = category.name
            category.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'Category {category_name} deleted successfully'
            })
        except ServiceCategory.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def reorder_categories(request):
    if request.method == 'POST':
        try:
            order_data = json.loads(request.body)
            
            with transaction.atomic():
                for item in order_data:
                    category = ServiceCategory.objects.get(id=item['id'])
                    category.order = item['order']
                    category.save()
                    
            return JsonResponse({
                'status': 'success',
                'message': 'Categories reordered successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def get_category_info(request, category_id):
    try:
        category = ServiceCategory.objects.get(id=category_id)
        data = {
            'name': category.name,
            'description': category.description,
            'is_active': category.is_active,
        }
        return JsonResponse(data)
    except ServiceCategory.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

@permission_required('authentication.is_manager', login_url='manager_login')
def get_service_info(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        data = {
            'name': service.name,
            'category': service.category.name,
            'rate': str(service.rate),
            'min_order': service.min_order,
            'max_order': service.max_order,
            'description': service.description,
            'status': service.status,
            'is_drip_feed': service.is_drip_feed
        }
        return JsonResponse(data)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)

@permission_required('authentication.is_manager', login_url='manager_login')
def add_payment_method(request):
    if request.method == 'POST':
        try:
            # Log the incoming request data
            logger.info(f"Received payment method data: {request.POST}")
            
            # Validate required fields
            required_fields = ['name', 'type', 'min_amount', 'max_amount', 'fee_type', 'fee_amount']
            for field in required_fields:
                if not request.POST.get(field):
                    raise ValueError(f"Missing required field: {field}")

            # Create payment method
            payment_method = PaymentMethod.objects.create(
                name=request.POST.get('name'),
                type=request.POST.get('type'),
                min_amount=Decimal(request.POST.get('min_amount')),
                max_amount=Decimal(request.POST.get('max_amount')),
                fee_type=request.POST.get('fee_type'),
                fee_percentage=Decimal(request.POST.get('fee_amount', '0')),
                is_active=request.POST.get('is_active') == 'on',
                test_mode=request.POST.get('test_mode') == 'on'
            )
            
            # Handle automatic payment method credentials
            if request.POST.get('type') == 'automatic':
                payment_method.client_id = request.POST.get('client_id')
                payment_method.client_secret = request.POST.get('client_secret')
                payment_method.save()

            logger.info(f"Successfully created payment method: {payment_method.name}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment method added successfully',
                'payment_method': {
                    'id': payment_method.id,
                    'name': payment_method.name,
                    'type': payment_method.type
                }
            })
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error creating payment method: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error creating payment method: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def toggle_payment_method(request, method_id):
    if request.method == 'POST':
        try:
            method = PaymentMethod.objects.get(id=method_id)
            method.is_active = not method.is_active
            method.save()
            
            logger.info(f"Payment method {method.name} status toggled to {method.is_active}")
            
            return JsonResponse({
                'status': 'success',
                'is_active': method.is_active
            })
        except PaymentMethod.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Payment method not found'
            }, status=404)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def delete_payment_method(request, method_id):
    if request.method == 'POST':
        try:
            method = PaymentMethod.objects.get(id=method_id)
            method_name = method.name
            method.delete()
            
            logger.info(f"Payment method {method_name} deleted successfully")
            
            return JsonResponse({
                'status': 'success',
                'message': f'Payment method {method_name} deleted successfully'
            })
        except PaymentMethod.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Payment method not found'
            }, status=404)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def get_payment_method(request, method_id):
    try:
        method = PaymentMethod.objects.get(id=method_id)
        data = {
            'name': method.name,
            'type': method.type,
            'min_amount': str(method.min_amount),
            'max_amount': str(method.max_amount),
            'fee_type': method.fee_type,
            'fee_percentage': str(method.fee_percentage),
            'fee_fixed': str(method.fee_fixed),
            'is_active': method.is_active,
            'test_mode': method.test_mode
        }
        return JsonResponse(data)
    except PaymentMethod.DoesNotExist:
        return JsonResponse({'error': 'Payment method not found'}, status=404)

@permission_required('authentication.is_manager', login_url='manager_login')
def edit_payment_method(request, method_id):
    if request.method == 'POST':
        try:
            method = PaymentMethod.objects.get(id=method_id)
            
            # Update fields
            method.name = request.POST.get('name')
            method.type = request.POST.get('type')
            method.min_amount = Decimal(request.POST.get('min_amount'))
            method.max_amount = Decimal(request.POST.get('max_amount'))
            method.fee_type = request.POST.get('fee_type')
            method.fee_percentage = Decimal(request.POST.get('fee_amount', '0'))
            method.is_active = request.POST.get('is_active') == 'on'
            method.test_mode = request.POST.get('test_mode') == 'on'
            
            # Save changes
            method.save()
            
            logger.info(f"Payment method {method.name} updated successfully")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment method updated successfully'
            })
            
        except PaymentMethod.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Payment method not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error updating payment method: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def view_transaction(request, transaction_id):
    try:
        transaction = Transactions.objects.select_related('user').get(id=transaction_id)
        data = {
            'id': transaction.id,
            'user': transaction.user.email,
            'amount': str(transaction.amount),
            'balance': str(transaction.user.balance),
            'payment_method': transaction.payment_method or '-',
            'transaction_id': transaction.transaction_id or '-',
            'status': transaction.status,
            'note': transaction.notes if hasattr(transaction, 'notes') else transaction.description if hasattr(transaction, 'description') else '-',
            'created_at': transaction.created.strftime('%Y-%m-%d %H:%M:%S'),
            'fee': str(transaction.fee) if hasattr(transaction, 'fee') else '0.00'
        }
        return JsonResponse(data)
    except Transactions.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        print(f"Error in view_transaction: {str(e)}")  # For debugging
        return JsonResponse({'error': 'Error loading transaction details'}, status=500)

@permission_required('authentication.is_manager', login_url='manager_login')
def approve_transaction(request, transaction_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Use Django's transaction.atomic() for atomic operations
                txn = Transactions.objects.select_for_update().get(id=transaction_id)
                
                if txn.status != 'waiting':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Transaction cannot be approved'
                    }, status=400)
                
                # Update transaction status
                txn.status = 'completed'
                txn.save()
                
                # Add amount to user's balance
                user = txn.user
                user.balance = user.balance + txn.amount
                user.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Transaction approved successfully'
                })
                
        except Transactions.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Transaction not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


@permission_required('authentication.is_manager', login_url='manager_login')
def cancel_transaction(request, transaction_id):
    if request.method == 'POST':
        try:
            txn = Transactions.objects.get(id=transaction_id)
            
            if txn.status != 'waiting':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Transaction cannot be cancelled'
                }, status=400)
            
            txn.status = 'cancelled'
            txn.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Transaction cancelled successfully'
            })
            
        except Transactions.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Transaction not found'
            }, status=404)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@permission_required('authentication.is_manager', login_url='manager_login')
def export_transactions(request):
    import csv
    from django.http import HttpResponse
    
    # Get filtered transactions
    transactions = Transactions.objects.select_related('user').all()
    
    # Apply filters (same as in payments view)
    # ... (copy filter logic from payments view)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow([
        'Transaction ID', 'User', 'Amount', 'Fee', 'Total Amount',
        'Payment Method', 'Status', 'Created', 'Description'
    ])
    
    # Write data
    for transaction in transactions:
        writer.writerow([
            transaction.transaction_id,
            transaction.user.email,
            transaction.amount,
            transaction.fee,
            transaction.total_amount,
            transaction.payment_method,
            transaction.status,
            transaction.created.strftime('%Y-%m-%d %H:%M:%S'),
            transaction.description
        ])
    
    return response

@permission_required('authentication.is_manager', login_url='manager_login')
def get_order_info(request, order_id):
    logger.debug(f"Fetching order info for ID: {order_id}")  # Debug log
    try:
        # Use select_related to optimize the query
        order = Order.objects.select_related('user', 'service').get(id=order_id)
        
        data = {
            'id': order.id,
            'status': order.status,
            'created_at': order.created.isoformat() if order.created else None,
            'updated_at': order.updated.isoformat() if order.updated else None,
            'charge': str(order.price),
            'service': order.service.name if order.service else 'N/A',
            'quantity': order.quantity,
            'link': order.link,
            'user_email': order.user.email if order.user else 'N/A',
        }
        logger.debug(f"Returning order data: {data}")  # Debug log
        return JsonResponse(data)
        
    except Order.DoesNotExist:
        logger.error(f"Order not found: {order_id}")
        return JsonResponse({
            'error': 'Order not found'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        return JsonResponse({
            'error': f'Error fetching order details: {str(e)}'
        }, status=500)

@login_required
@require_POST
def complete_order(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Check if user has permission to complete orders
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to complete orders'
            }, status=403)

        # Check if order can be completed
        if order.status not in ['pending', 'processing']:
            return JsonResponse({
                'success': False,
                'message': 'This order cannot be completed'
            }, status=400)

        # Update order status
        order.status = 'completed'
        order.save()

        return JsonResponse({
            'success': True,
            'message': 'Order marked as completed successfully'
        })
    except Exception as e:
        logger.error(f"Error completing order {order_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
    


@login_required
@require_POST
def cancel_order(request, order_id):

    logger.info(f"Request method: {request.method}")
    logger.info(f"CSRF Token: {request.META.get('HTTP_X_CSRFTOKEN')}")

    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Check if user has permission to cancel orders
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to cancel orders'
            }, status=403)

        # Check if order can be canceled
        if order.status not in ['processing', 'pending']:
            return JsonResponse({
                'success': False,
                'message': 'This order cannot be canceled'
            }, status=400)

        # Update order status
        order.status = 'canceled'
        order.save()

        return JsonResponse({
            'success': True,
            'message': 'Order marked as canceled successfully'
        })
    except Exception as e:
        logger.error(f"Error canceling order {order_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)










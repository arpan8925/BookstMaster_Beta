from django.shortcuts import render

from django.contrib.auth.decorators import permission_required

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
from .models import Transaction

from managerdashboard.models import Provider, ProviderTransaction



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

    context = {

        'active_tab': 'orders',

    }

    return render(request, 'managerdashboard/orders.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def services(request):

    context = {

        'active_tab': 'services',

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

    context = {

        'active_tab': 'payments',

    }

    return render(request, 'managerdashboard/payments.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def settings(request):

    context = {

        'active_tab': 'settings',

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
                Transaction.objects.create(
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







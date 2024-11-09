from django.shortcuts import render

from django.contrib.auth.decorators import permission_required

from django.db.models import Count, Sum

from authentication.models import User

from user_dashboard.models import Ticket

from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail as django_send_mail
from django.conf import settings



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

def reports(request):

    context = {

        'active_tab': 'reports',

    }

    return render(request, 'managerdashboard/reports.html', context)



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

    tickets = Ticket.objects.all().order_by('-created_at')

    context = {

        'active_tab': 'tickets',

        'tickets': tickets,

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

def subscribers(request):

    context = {

        'active_tab': 'subscribers',

    }

    return render(request, 'managerdashboard/subscribers.html', context)



@permission_required('authentication.is_manager', login_url='manager_login')

def providers(request):

    context = {

        'active_tab': 'providers',

    }

    return render(request, 'managerdashboard/providers.html', context)



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
        try:
            user = User.objects.get(id=user_id)
            # Add your fund addition logic here
            messages.success(request, f'${amount} added to {user.username}\'s account')
        except User.DoesNotExist:
            messages.error(request, 'User not found')
    return redirect('managerdashboard:users')



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







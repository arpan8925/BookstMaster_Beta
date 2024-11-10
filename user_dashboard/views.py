from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, TicketMessage
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'active_tab': 'support',
        'tickets': tickets,
        'open_count': tickets.filter(status='open').count(),
        'in_progress_count': tickets.filter(status='in_progress').count(),
        'closed_count': tickets.filter(status='closed').count(),
    }
    return render(request, 'user_dashboard/tickets/ticket_list.html', context)

@login_required
def ticket_create(request):
    context = {
        'active_tab': 'support'
    }
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        priority = request.POST.get('priority')
        
        if subject and message:
            ticket = Ticket.objects.create(
                user=request.user,
                subject=subject,
                message=message,
                priority=priority
            )
            messages.success(request, 'Ticket created successfully!')
            return redirect('ticket_detail', pk=ticket.pk)
    return render(request, 'user_dashboard/tickets/ticket_create.html', context)

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=message
            )
            messages.success(request, 'Reply added successfully!')
            return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'user_dashboard/tickets/ticket_detail.html', {
        'ticket': ticket,
        'replies': ticket.messages.all()
    })

@login_required
def dashboard(request):
    context = {
        'active_tab': 'dashboard'
    }
    return render(request, 'user_dashboard/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        
        # Update basic information
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.timezone = request.POST.get('timezone', 'UTC')
        
        # Handle password change
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password:
            if password == confirm_password:
                user.set_password(password)
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully!')
            else:
                messages.error(request, 'Passwords do not match!')
                return redirect('user_profile')
        
        user.save()
        return render(request, 'user_dashboard/profile.html', {
            'active_tab': 'profile',
            'show_success_alert': True
        })
        
    return render(request, 'user_dashboard/profile.html', {'active_tab': 'profile'})

@login_required
def profile_more(request):
    if request.method == 'POST':
        user = request.user
        
        # Update additional information
        user.website = request.POST.get('website')
        user.phone = request.POST.get('phone')
        user.skype = request.POST.get('skype')
        user.whatsapp = request.POST.get('whatsapp')
        user.address = request.POST.get('address')
        user.city = request.POST.get('city')
        
        user.save()
        return render(request, 'user_dashboard/profile.html', {
            'active_tab': 'profile',
            'show_additional_success_alert': True
        })
        
    return redirect('user_profile')

@login_required
def security_settings(request):
    context = {
        'active_tab': 'security'
    }
    return render(request, 'user_dashboard/security.html', context)

@login_required
def posts(request):
    context = {
        'active_tab': 'posts'
    }
    return render(request, 'user_dashboard/posts.html', context)

@login_required
def favorites(request):
    context = {
        'active_tab': 'favorites'
    }
    return render(request, 'user_dashboard/favorites.html', context)

@login_required
def user_messages(request):
    context = {
        'active_tab': 'messages'
    }
    return render(request, 'user_dashboard/messages.html', context)

@login_required
def notifications(request):
    context = {
        'active_tab': 'notifications'
    }
    return render(request, 'user_dashboard/notifications.html', context)

@login_required
def preferences(request):
    context = {
        'active_tab': 'preferences'
    }
    return render(request, 'user_dashboard/preferences.html', context)

@login_required
def new_order(request):
    context = {
        'active_tab': 'order'
    }
    if request.method == 'POST':
        # Handle form submission here
        pass
    return render(request, 'user_dashboard/order/new_order.html', context)

@login_required
def order_log(request):
    orders = [{
        'order_id': '390480',
        'api_order': 'API123',
        'user': 'john_doe',
        'details': 'YouTube subscribers lifetime - 750',
        'created': '2024-11-04 05:25:04',
        'status': 'In Progress',
        'api_response': 'Success',
    }]
    context = {
        'active_tab': 'order',
        'orders': orders
    }
    return render(request, 'user_dashboard/order/order_log.html', context)

@login_required
def services(request):
    services = [{
        'id': '26192',
        'name': 'Facebook page like + Followers Non Drop All Type of page',
        'rate': '0.28',
        'min_max': '100 / 50000',
        'details': 'Details'
    }]
    context = {
        'active_tab': 'services',
        'services': services
    }
    return render(request, 'user_dashboard/services.html', context)

@login_required
def api_documentation(request):
    api_data = {
        'api_key': '61AMKvJNRmP2M2JjFkTWZwzsnlLzNzpl',
        'api_url': 'https://boostmasterbdpro.com/api/v1',
        'endpoints': []
    }
    context = {
        'active_tab': 'api',
        'api_data': api_data
    }
    return render(request, 'user_dashboard/api_documentation.html', context)

@login_required
def add_funds(request):
    context = {
        'active_tab': 'add_funds',
        'payment_methods': [
            {'id': 'perfectmoney', 'name': 'Perfectmoney'},
            {'id': 'bkash', 'name': 'Bkash'},
            {'id': 'manual', 'name': 'Manual Payment'},
        ]
    }
    return render(request, 'user_dashboard/add_funds.html', context)

@login_required
def transaction_logs(request):
    transactions = [
        {
            'id': 1,
            'amount': 4.08,
            'payment_method': 'Bkash',
            'status': 'Waiting for buyer funds...',
            'created': '2023-01-20 18:03:24'
        }
    ]
    context = {
        'active_tab': 'transactions',
        'transactions': transactions
    }
    return render(request, 'user_dashboard/transaction_logs.html', context)

@login_required
def tickets(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-created')
    
    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_number = request.GET.get('page')
    tickets_page = paginator.get_page(page_number)
    
    context = {
        'tickets': tickets_page,
        'active_tab': 'tickets'
    }
    return render(request, 'user_dashboard/tickets.html', context)

@login_required
def create_ticket(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        priority = request.POST.get('priority', 'medium')
        
        if subject and content:
            ticket = Ticket.objects.create(
                user=request.user,
                subject=subject,
                description=content,
                priority=priority
            )
            
            # Create initial message
            TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=content
            )
            
            return JsonResponse({'status': 'success', 'ticket_id': ticket.id})
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    messages = ticket.messages.all().order_by('created')  # Changed from replies to messages
    
    context = {
        'ticket': ticket,
        'messages': messages,
        'active_tab': 'tickets'
    }
    return render(request, 'user_dashboard/view_ticket.html', context)

@login_required
@require_POST
def reply_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    message = request.POST.get('message')
    
    if message:
        TicketMessage.objects.create(
            ticket=ticket,
            user=request.user,
            message=message
        )
        
        # Update ticket status if needed
        if ticket.status == 'closed':
            ticket.status = 'pending'
            ticket.save()
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Message content is required'})

@login_required
@require_POST
def close_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    ticket.status = 'closed'
    ticket.save()
    return JsonResponse({'status': 'success'})

@login_required
def generate_new_api_key(request):
    if request.method == 'POST':
        request.user.generate_api_key()
        return JsonResponse({'status': 'success', 'api_key': request.user.api_key})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

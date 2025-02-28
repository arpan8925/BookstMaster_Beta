from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, TicketMessage, Order
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
import secrets
from managerdashboard.models import PaymentMethod, Transactions
from decimal import Decimal
from django.db import connection
from django.http import JsonResponse
from django.db import connection
from .forms import AddFundsForm

def calculate_fee(payment_method, amount):
    if payment_method.fee_type == 'percentage':
        return amount * (payment_method.fee_percentage / Decimal('100'))
    elif payment_method.fee_type == 'fixed':
        return payment_method.fee_fixed
    else:
        return (amount * (payment_method.fee_percentage / Decimal('100'))) + payment_method.fee_fixed

@login_required
def search_services(request):
    query = request.GET.get('q', '').lower()  # Get the search query from the request
    if query:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, s.name, s.price, s.desc, s.min, s.max,
                       c.id AS category_id, c.name AS category_name
                FROM services s
                INNER JOIN categories c ON s.cate_id = c.id
                WHERE s.status = 1 AND LOWER(s.name) LIKE %s
                ORDER BY c.name, s.name
            """, [f"%{query}%"])
            columns = [col[0] for col in cursor.description]
            services = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Structure the result as JSON
        return JsonResponse({'results': services})
    return JsonResponse({'results': []})  # Return empty if no query is provided or no matches found


@login_required
def dashboard(request):
    user = request.user
    full_name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username

    # Fetch services and their categories from the database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.id, s.name, s.price, s.desc, s.min, s.max,
                   c.id AS category_id, c.name AS category_name
            FROM services s
            INNER JOIN categories c ON s.cate_id = c.id
            WHERE s.status = 1 
            ORDER BY c.name, s.name
        """)
        columns = [col[0] for col in cursor.description]
        services = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Organize services by category
    categories = {}
    for service in services:
        cat_id = service['category_id']
        cat_name = service['category_name']
        if cat_id not in categories:
            categories[cat_id] = {
                'name': cat_name,
                'services': []
            }
        categories[cat_id]['services'].append(service)

    context = {
        'active_tab': 'dashboard',
        'categories': categories,  # Pass categories with their services
        'user_name': full_name,
        'user_level': user.get_level_display(),
        'user_balance': user.balance,
        'user_spent': user.spent,
    }
    
    return render(request, 'user_dashboard/index.html', context)

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
def order_log(request):
    user = request.user
    full_name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username 
    # Get filter parameters
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    # Get all orders for the user
    orders = Order.objects.filter(user=request.user)
    
    # Apply filters
    if status:
        orders = orders.filter(status=status)
    if date_from:
        orders = orders.filter(created__gte=date_from)
    if date_to:
        orders = orders.filter(created__lte=date_to)
    if search:
        orders = orders.filter(
            models.Q(service__name__icontains=search) |
            models.Q(link__icontains=search)
        )
    
    # Calculate statistics
    total_orders = orders.count()
    completed_orders = orders.filter(status='completed').count()
    pending_orders = orders.filter(status='pending').count()
    failed_orders = orders.filter(status='failed').count()
    processing_orders = orders.filter(status='processing').count()
    canceled_orders = orders.filter(status='canceled').count()
    refunded_orders = orders.filter(status='refunded').count()
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Handle export
    if request.GET.get('export'):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Service', 'Link', 'Quantity', 'Price', 'Status', 'Created'])
        
        for order in orders:
            writer.writerow([
                order.id,
                order.service.name,
                order.link,
                order.quantity,
                order.price,
                order.status,
                order.created.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    context = {
        'active_tab': 'order',
        'orders': page_obj,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'failed_orders': failed_orders,
        'processing_orders': processing_orders,
        'canceled_orders': canceled_orders,
        'refunded_orders': refunded_orders,
        'filter_status': status,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
        'filter_search': search,
        'user_level': user.get_level_display(),
        'user_balance': user.balance,
        'user_name': full_name,
    }
    return render(request, 'user_dashboard/orders.html', context)

@login_required
def services_view(request):
    user = request.user
    full_name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username 

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, price, desc, min, max, add_type AS category_id 
            FROM services
            WHERE status = 1 
            ORDER BY add_type, id
        """)
        columns = [col[0] for col in cursor.description]
        services = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Multiply the price by 100 for each service
    for service in services:
        service['price'] = service['price'] * 1000

    context = {
        'active_tab': 'services',
        'services': services,  # For general listing
        'user_level': user.get_level_display(),
        'user_balance': user.balance,
        'user_name': full_name,
    }

    return render(request, 'user_dashboard/Services.html', context)


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
    user = request.user
    payment_methods = PaymentMethod.objects.filter(is_active=True).order_by('name')

    form = AddFundsForm(request.POST or None, payment_methods=payment_methods)

    if request.method == 'POST' and form.is_valid():
        payment_method = form.cleaned_data['payment_method']
        amount = form.cleaned_data['amount']
        terms = form.cleaned_data['terms']

        if not terms:
            form.add_error('terms', 'You must agree to the Terms & Conditions.')
            return render(request, 'user_dashboard/AddFund.html', {'form': form, 'payment_methods': payment_methods})

        fee = calculate_fee(payment_method, amount)
        total_amount = amount + fee

        # Handle manual payment processing
        if payment_method.type == 'manual':
            transaction = Transactions.objects.create(
                uid=user,  # Pass the User instance here
                amount=amount,
                fee=fee,
                total_amount=total_amount,
                payment_method=payment_method,
                status='waiting',
                description=f"Manual payment via {payment_method.name}"
            )
            messages.success(request, f'Transaction initiated successfully. Your transaction ID is {transaction.transaction_id}. Please follow the instructions to complete the payment.')
            return redirect('transaction_detail', transaction_id=transaction.transaction_id)

        # Handle automatic payment processing
        else:
            transaction = Transactions.objects.create(
                uid=user,  # Pass the User instance here
                amount=amount,
                fee=fee,
                total_amount=total_amount,
                payment_method=payment_method,
                status='waiting',
                description=f"Payment via {payment_method.name}"
            )
            messages.success(request, f'Transaction initiated successfully. Your transaction ID is {transaction.transaction_id}')
            return redirect('transaction_detail', transaction_id=transaction.transaction_id)

    return render(request, 'user_dashboard/AddFund.html', {
        'form': form,
        'payment_methods': payment_methods,
        'user': user,
        'user_balance': user.balance
    })

@login_required
def transaction_logs(request):
    # Get all transactions for the current user, ordered by creation date
    transactions = Transactions.objects.filter(user=request.user).order_by('-created')
    
    # Add pagination
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    transactions_page = paginator.get_page(page_number)
    
    context = {
        'active_tab': 'transactions',
        'transactions': transactions_page,
        'total_transactions': transactions.count(),
        'total_amount': sum(t.total_amount for t in transactions),
        'completed_transactions': transactions.filter(status='completed').count(),
        'pending_transactions': transactions.filter(status='waiting').count()
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
def generate_api_key(request):
    if request.method == 'POST':
        try:
            # Generate new API key
            new_key = secrets.token_urlsafe(32)
            request.user.api_key = new_key
            request.user.save(update_fields=['api_key'])
            
            # Return to profile page with custom alert
            # Removed the messages.success() call to prevent double alerts
            return render(request, 'user_dashboard/profile.html', {
                'active_tab': 'profile',
                'show_success_alert': True,  # This will trigger our custom alert
                'success_message': 'New API key generated successfully!'  # Custom message
            })
            
        except Exception as e:
            print(f"Error generating API key: {str(e)}")  # For debugging
            return render(request, 'user_dashboard/profile.html', {
                'active_tab': 'profile',
                'show_error_alert': True,
                'error_message': 'Failed to generate new API key'
            })
    
    return redirect('user_profile')

@login_required
def process_payment(request, method_id):
    if request.method == 'POST':
        try:
            method = PaymentMethod.objects.get(id=method_id, is_active=True)
            amount = Decimal(request.POST.get('amount', '0'))
            
            if amount < method.min_amount or amount > method.max_amount:
                messages.error(request, 'Invalid amount')
                return redirect('add_funds')
            
            fee = Decimal('0')
            if method.fee_type == 'percentage':
                fee = amount * (method.fee_percentage / Decimal('100'))
            elif method.fee_type == 'fixed':
                fee = method.fee_fixed
            else:
                fee = (amount * (method.fee_percentage / Decimal('100'))) + method.fee_fixed
            
            # Create transaction with description
            transaction = Transactions.objects.create(
                user=request.user,
                amount=amount,
                fee=fee,
                payment_method=method.name,
                status='waiting',
                description=f"Payment via {method.name}"  # Using description instead of notes
            )
            
            if method.type == 'automatic':
                payment_handler = get_payment_handler(method.name)
                if payment_handler:
                    return payment_handler.initialize_payment(transaction)
            else:
                messages.success(
                    request, 
                    f'Transaction initiated successfully. Your transaction ID is {transaction.transaction_id}'
                )
                return redirect('transaction_detail', transaction_id=transaction.transaction_id)
            
        except PaymentMethod.DoesNotExist:
            messages.error(request, 'Invalid payment method')
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
    
    return redirect('add_funds')

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transactions, transaction_id=transaction_id, uid=request.user.uid)
    return render(request, 'user_dashboard/transaction_detail.html', {'transaction': transaction})

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

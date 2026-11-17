from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import BarLocation
from bar_catalog.models import MenuItem
from .models import TableSession, OrderItem

@login_required
def qr_generator_view(request):
    user_bars = BarLocation.objects.filter(owner=request.user)
    active_bar = user_bars.first()
    return render(request, 'orders/qr_generator.html', {'user_bars': user_bars, 'active_bar': active_bar})

def client_menu_view(request, bar_id):
    bar = get_object_or_404(BarLocation, id=bar_id)
    table_number = request.GET.get('mesa', 'Balcão')
    is_fixed_bar = request.GET.get('bar_fixo') == '1'
    show_price = request.GET.get('preco') == 'sim'
    
    # Busca sessão ativa para mesas ou bar fixo
    active_session = TableSession.objects.filter(bar=bar, table_number=table_number, is_active=True).first()
    
    error_msg = None
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start_session':
            client_name = request.POST.get('client_name')
            entered_password = request.POST.get('password', '').strip()
            
            if active_session:
                if not is_fixed_bar and entered_password != active_session.table_password:
                    error_msg = "Senha incorreta para esta mesa!"
                else:
                    request.session[f'session_{bar.id}_{table_number}'] = active_session.id
                    return redirect(f'/orders/client-menu/{bar.id}/?mesa={table_number}&preco={"sim" if show_price else "nao"}{"&bar_fixo=1" if is_fixed_bar else ""}')
            else:
                new_session = TableSession.objects.create(
                    bar=bar, table_number=table_number, client_name=client_name, is_active=True, is_fixed_bar=is_fixed_bar
                )
                request.session[f'session_{bar.id}_{table_number}'] = new_session.id
                return redirect(f'/orders/client-menu/{bar.id}/?mesa={table_number}&preco={"sim" if show_price else "nao"}{"&bar_fixo=1" if is_fixed_bar else ""}')
                
        elif action == 'place_order':
            session_id = request.session.get(f'session_{bar.id}_{table_number}')
            session = get_object_or_404(TableSession, id=session_id, is_active=True)
            recipe_id = request.POST.get('recipe_id')
            quantity = int(request.POST.get('quantity', 1))
            observation = request.POST.get('observation', '')
            recipe = get_object_or_404(MenuItem, id=recipe_id)
            
            OrderItem.objects.create(session=session, recipe=recipe, quantity=quantity, observation=observation)
            return redirect(f'/orders/client-menu/{bar.id}/?mesa={table_number}&preco={"sim" if show_price else "nao"}{"&bar_fixo=1" if is_fixed_bar else ""}')

    current_session_id = request.session.get(f'session_{bar.id}_{table_number}')
    current_session = TableSession.objects.filter(id=current_session_id, is_active=True).first() if current_session_id else active_session

    session_orders = []
    session_total = 0
    if current_session:
        session_orders = current_session.orders.all()
        session_total = sum(o.quantity * o.recipe.price for o in session_orders)

    category = request.GET.get('category', 'Todos')
    query = MenuItem.objects.filter(is_public=True)
    if category != 'Todos':
        query = query.filter(category=category)
    recipes = query.all()
    categories = ['Todos', 'Refrescantes', 'Fortes', 'Doces & Frutados', 'Cítricos', 'Tropicais', 'Aperitivos']
    
    return render(request, 'orders/client_menu.html', {
        'bar': bar,
        'table_number': table_number,
        'is_fixed_bar': is_fixed_bar,
        'show_price': show_price,
        'active_session': active_session,
        'current_session': current_session,
        'session_orders': session_orders,
        'session_total': session_total,
        'recipes': recipes,
        'categories': categories,
        'current_cat': category,
        'error_msg': error_msg,
    })

@login_required
def manage_sessions_view(request):
    user_bars = BarLocation.objects.filter(owner=request.user)
    active_bar = user_bars.first()
    sessions = TableSession.objects.filter(bar=active_bar, is_active=True).order_by('-created_at')
    
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        session = get_object_or_404(TableSession, id=session_id)
        session.is_active = False
        session.save()
        return redirect('manage_sessions')
        
    session_data = []
    for s in sessions:
        items = s.orders.all()
        total = sum(i.quantity * i.recipe.price for i in items)
        session_data.append({'session': s, 'items': items, 'total': total})
        
    return render(request, 'orders/manage_sessions.html', {'session_data': session_data, 'user_bars': user_bars, 'active_bar': active_bar})

@login_required
def live_orders_view(request):
    user_bars = BarLocation.objects.filter(owner=request.user)
    active_bar = user_bars.first()
    orders = OrderItem.objects.filter(session__bar=active_bar, session__is_active=True).order_by('-created_at')
    
    if request.method == 'POST':
        order = get_object_or_404(OrderItem, id=request.POST.get('order_id'))
        if order.status == 'Pendente':
            order.status = 'Pronto'
        elif order.status == 'Pronto':
            order.status = 'Entregue'
        else:
            order.status = 'Pendente'
        order.save()
        return redirect('live_orders')
        
    return render(request, 'orders/live_orders.html', {'orders': orders, 'user_bars': user_bars, 'active_bar': active_bar})
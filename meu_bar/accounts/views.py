from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import BarLocation

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Cria automaticamente um bar padrão "Residencial" para o novo usuário
            BarLocation.objects.create(owner=user, name="Meu Bar de Casa", bar_type="home")
            login(request, user)
            return redirect('recipes_list')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('recipes_list')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def manage_bars(request):
    user_bars = BarLocation.objects.filter(owner=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        bar_type = request.POST.get('bar_type')
        total_tables = int(request.POST.get('total_tables', 0) or 0)
        
        BarLocation.objects.create(
            owner=request.user,
            name=name,
            bar_type=bar_type,
            total_tables=total_tables
        )
        return redirect('manage_bars')
        
    return render(request, 'accounts/bars_manage.html', {'user_bars': user_bars})
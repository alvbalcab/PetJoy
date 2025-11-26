from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, PerfilForm


def registro_view(request):
    """Vista de registro de nuevo cliente"""
    if request.user.is_authenticated:
        return redirect('core:inicio')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('core:inicio')
    else:
        form = RegistroForm()
    
    context = {'form': form}
    return render(request, 'clientes/registro.html', context)


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('core:inicio')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Buscar usuario por email
            from .models import Cliente
            try:
                user = Cliente.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    next_url = request.GET.get('next', 'core:inicio')
                    messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Email o contraseña incorrectos')
            except Cliente.DoesNotExist:
                messages.error(request, 'Email o contraseña incorrectos')
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'clientes/login.html', context)


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('core:inicio')


@login_required
def perfil_view(request):
    """Vista de perfil del usuario"""
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('clientes:perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'clientes/perfil.html', context)

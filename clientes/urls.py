from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'clientes'

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    # --- CAMBIO DE CONTRASEÑA (Usuario logueado) ---
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='clientes/password_change.html', 
             success_url='/cuenta/password_change/done/'
         ), 
         name='password_change'),
         
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='clientes/password_change_done.html'
         ), 
         name='password_change_done'),

    # --- RECUPERACIÓN DE CONTRASEÑA (Email System) ---
    
    # 1. Formulario para pedir el correo
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='clientes/password_reset_form.html',
             email_template_name='clientes/password_reset_email.html',
             subject_template_name='clientes/password_reset_subject.txt',
             success_url='/cuenta/password_reset/done/'
         ), 
         name='password_reset'),

    # 2. Mensaje de "Correo enviado"
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='clientes/password_reset_done.html'
         ), 
         name='password_reset_done'),

    # 3. Link mágico desde el correo (Formulario nueva clave)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='clientes/password_reset_confirm.html',
             success_url='/cuenta/reset/done/'
         ), 
         name='password_reset_confirm'),

    # 4. Mensaje de éxito final
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='clientes/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]

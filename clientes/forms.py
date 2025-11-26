from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente


class RegistroForm(UserCreationForm):
    """Formulario de registro de clientes"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    telefono = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    direccion = forms.CharField(
        required=True,
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de Envío *'})
    )
    ciudad = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad *'})
    )
    codigo_postal = forms.CharField(
        required=True,
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal *'})
    )
    
    class Meta:
        model = Cliente
        fields = ['email', 'first_name', 'last_name', 'telefono', 'direccion', 'ciudad', 'codigo_postal', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['ciudad'].widget.attrs.update({'class': 'form-control'})
        self.fields['codigo_postal'].widget.attrs.update({'class': 'form-control'})
                                                         
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Usar email como username
        user.email = self.cleaned_data['email']
        user.telefono = self.cleaned_data['telefono']
        user.direccion = self.cleaned_data['direccion']
        user.ciudad = self.cleaned_data['ciudad']
        user.codigo_postal = self.cleaned_data['codigo_postal']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Formulario de login"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )


class PerfilForm(forms.ModelForm):
    """Formulario de edición de perfil"""
    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion', 'ciudad', 'codigo_postal']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
        }

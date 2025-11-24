from django import forms
from productos.models import Producto, ImagenProducto
from pedidos.models import Pedido

class ProductoForm(forms.ModelForm):
    imagen_principal = forms.ImageField(required=False, label="Imagen Principal")

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'precio_oferta', 'categoria', 'marca', 'stock', 'esta_disponible', 'genero'] 
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_oferta': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'esta_disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EstadoPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
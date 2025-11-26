from django.shortcuts import render
from productos.models import Producto, Categoria
from core.models import DatosEmpresa
from django.core.mail import send_mail
from django.contrib import messages


def inicio(request):
    """Página de inicio/escaparate"""
    productos_destacados = Producto.objects.filter(es_destacado=True, esta_disponible=True)[:8]
    categorias = Categoria.objects.all()[:6]
    datos_empresa = DatosEmpresa.get_datos()
    
    context = {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'datos_empresa': datos_empresa,
    }
    return render(request, 'core/inicio.html', context)


def acerca_de(request):
    """Página acerca de"""
    datos_empresa = DatosEmpresa.get_datos()
    context = {
        'datos_empresa': datos_empresa,
    }
    return render(request, 'core/acerca_de.html', context)


def contacto(request):
    """Página de contacto"""
    datos_empresa = DatosEmpresa.get_datos()
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')
        
        # Enviar email
        try:
            asunto = f'Contacto desde la web - {nombre}'
            cuerpo = f'Nombre: {nombre}\nEmail: {email}\n\nMensaje:\n{mensaje}'
            send_mail(
                asunto,
                cuerpo,
                email,
                [datos_empresa.email],
                fail_silently=False,
            )
            messages.success(request, '¡Mensaje enviado correctamente! Te responderemos pronto.')
        except Exception as e:
            messages.error(request, 'Error al enviar el mensaje. Por favor, inténtalo de nuevo.')
    
    context = {
        'datos_empresa': datos_empresa,
    }
    return render(request, 'core/contacto.html', context)

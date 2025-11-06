from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from productos.models import Producto
from .carrito import Carrito
from .models import Pedido, ItemPedido
from .forms import DatosEnvioForm
from core.models import DatosEmpresa
from decimal import Decimal


def ver_carrito(request):
    """Vista del carrito de compra"""
    carrito = Carrito(request)
    context = {
        'carrito': carrito,
    }
    return render(request, 'pedidos/carrito.html', context)


def agregar_al_carrito(request, producto_id):
    """Agregar producto al carrito"""
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    
    cantidad = int(request.POST.get('cantidad', 1))
    talla = request.POST.get('talla', '')
    
    carrito.agregar(producto=producto, cantidad=cantidad, talla=talla)
    messages.success(request, f'{producto.nombre} añadido al carrito')
    
    return redirect(request.META.get('HTTP_REFERER', 'productos:catalogo'))


def actualizar_carrito(request, producto_id):
    """Actualizar cantidad de un producto en el carrito"""
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    
    cantidad = int(request.POST.get('cantidad', 1))
    talla = request.POST.get('talla', '')
    
    if cantidad > 0:
        carrito.agregar(producto=producto, cantidad=cantidad, talla=talla, actualizar_cantidad=True)
        messages.success(request, 'Carrito actualizado')
    else:
        carrito.eliminar(producto, talla=talla)
        messages.info(request, 'Producto eliminado del carrito')
    
    return redirect('pedidos:carrito')


def eliminar_del_carrito(request, producto_id):
    """Eliminar producto del carrito"""
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    talla = request.GET.get('talla', '')
    
    carrito.eliminar(producto, talla=talla)
    messages.info(request, f'{producto.nombre} eliminado del carrito')
    
    return redirect('pedidos:carrito')


def checkout(request):
    """Proceso de checkout"""
    carrito = Carrito(request)
    
    if len(carrito) == 0:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('productos:catalogo')
    
    if request.method == 'POST':
        form = DatosEnvioForm(request.POST)
        if form.is_valid():
            # Crear el pedido
            datos_empresa = DatosEmpresa.get_datos()
            
            subtotal = carrito.obtener_precio_total()
            envio = carrito.obtener_coste_envio()
            impuestos = carrito.obtener_impuestos()
            total = carrito.obtener_total_final()
            
            pedido = Pedido.objects.create(
                cliente=request.user if request.user.is_authenticated else None,
                nombre_cliente=form.cleaned_data['nombre'],
                apellidos_cliente=form.cleaned_data['apellidos'],
                email_cliente=form.cleaned_data['email'],
                telefono_cliente=form.cleaned_data['telefono'],
                direccion_envio=form.cleaned_data['direccion'],
                ciudad_envio=form.cleaned_data['ciudad'],
                codigo_postal_envio=form.cleaned_data['codigo_postal'],
                subtotal=subtotal,
                impuestos=impuestos,
                coste_entrega=envio,
                total=total,
                metodo_pago=form.cleaned_data['metodo_pago'],
                notas=form.cleaned_data.get('notas', ''),
            )
            
            # Crear los items del pedido
            for item in carrito:
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=item['producto'],
                    nombre_producto=item['producto'].nombre,
                    talla=item.get('talla', ''),
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    total=item['total'],
                )
                
                # Actualizar stock
                producto = item['producto']
                producto.stock -= item['cantidad']
                producto.save()
            
            # Enviar email de confirmación
            try:
                asunto = f'Confirmación de Pedido #{pedido.numero_pedido}'
                mensaje = render_to_string('pedidos/email_confirmacion.html', {
                    'pedido': pedido,
                    'datos_empresa': datos_empresa,
                })
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [pedido.email_cliente],
                    fail_silently=True,
                )
            except:
                pass
            
            # Limpiar el carrito
            carrito.limpiar()
            
            messages.success(request, f'¡Pedido realizado con éxito! Número de pedido: {pedido.numero_pedido}')
            return redirect('pedidos:confirmacion', pedido_id=pedido.numero_pedido)
    else:
        # Prellenar el formulario si el usuario está autenticado
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'nombre': request.user.first_name,
                'apellidos': request.user.last_name,
                'email': request.user.email,
                'telefono': request.user.telefono,
                'direccion': request.user.direccion,
                'ciudad': request.user.ciudad,
                'codigo_postal': request.user.codigo_postal,
            }
        form = DatosEnvioForm(initial=initial_data)
    
    context = {
        'form': form,
        'carrito': carrito,
    }
    return render(request, 'pedidos/checkout.html', context)


def confirmacion_pedido(request, pedido_id):
    """Página de confirmación del pedido"""
    pedido = get_object_or_404(Pedido, numero_pedido=pedido_id)
    context = {
        'pedido': pedido,
    }
    return render(request, 'pedidos/confirmacion.html', context)


def seguimiento_pedido(request):
    """Seguimiento de pedido por número"""
    pedido = None
    
    if request.method == 'POST':
        numero_pedido = request.POST.get('numero_pedido')
        email = request.POST.get('email')
        
        try:
            pedido = Pedido.objects.get(numero_pedido=numero_pedido, email_cliente=email)
        except Pedido.DoesNotExist:
            messages.error(request, 'No se encontró el pedido con esos datos')
    
    context = {
        'pedido': pedido,
    }
    return render(request, 'pedidos/seguimiento.html', context)


@login_required
def mis_pedidos(request):
    """Lista de pedidos del usuario autenticado"""
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_creacion')
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'pedidos/mis_pedidos.html', context)

def email_confirmacion(request):
    pedido = get_object_or_404(Pedido, numero_pedido=1)  # Cambiar por un ID válido para pruebas
    datos_empresa = DatosEmpresa.get_datos()
    
    asunto = f'Confirmación de Pedido #{pedido.numero_pedido}'
    mensaje = render_to_string('pedidos/email_confirmacion.html', {
        'pedido': pedido,
        'datos_empresa': datos_empresa,
    })
    
    context = {
        'asunto': asunto,
        'mensaje': mensaje,
    }
    return render(request, 'pedidos/email_preview.html', context)
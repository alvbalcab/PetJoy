import stripe
from django.http import JsonResponse
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
from django.db import transaction
import threading

stripe.api_key = settings.STRIPE_SECRET_KEY

def ver_carrito(request):
    """Muestra la página completa de la cesta."""
    carrito_obj = Carrito(request)
    datos_empresa = DatosEmpresa.get_datos() # Usa el método get_datos del modelo
    
    context = {
        'carrito': carrito_obj,
        'datos_empresa': datos_empresa
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
    """
    Captura los datos de envío y contacto. 
    Si el usuario está registrado, precarga datos. Si es anónimo, solicita todos.
    Guarda los datos en la sesión para la creación del pedido posterior.
    """
    carrito = Carrito(request)
    
    if len(carrito) == 0:
        # No se puede ir al checkout con el carrito vacío
        return redirect('pedidos:detalle_carrito')

    datos_iniciales = {}
    if request.user.is_authenticated:
        # Requisito 1: Pre-cargar datos del cliente autenticado
        datos_iniciales = {
            'nombre': request.user.first_name,
            'apellidos': request.user.last_name,
            'email': request.user.email,
            'telefono': request.user.telefono or '',
            'direccion': request.user.direccion or '',
            'ciudad': request.user.ciudad or '',
            'codigo_postal': request.user.codigo_postal or '',
        }

    if request.method == 'POST':
        form = DatosEnvioForm(request.POST)
        if form.is_valid():
            # PASO CLAVE: Guardar datos de envío en la sesión una vez validados
            request.session['datos_envio_checkout'] = form.cleaned_data
            
            # Determinar el método de pago (Stripe o Contrareembolso)
            # El campo 'metodo_pago_final' viene del botón pulsado en checkout.html
            metodo_pago_final = request.POST.get('metodo_pago_final') 
            
            if metodo_pago_final == 'contrareembolso':
                # Si se elige contrareembolso, redirigir a la vista de Contrareembolso
                # No necesitamos el decorador @transaction.atomic si ya lo tienes en 'pago_contrareembolso'
                return redirect('pedidos:pago_contrareembolso') 
            
            # Por defecto (o si es 'tarjeta'), redirigir a la sesión de Stripe
            return redirect('pedidos:crear_sesion_stripe')
        
        # Si el formulario NO es válido, el código continúa hacia render y muestra errores
    else:
        form = DatosEnvioForm(initial=datos_iniciales) # Muestra el formulario precargado

    context = {
        'form': form,
        'carrito': carrito,
    }
    return render(request, 'pedidos/checkout.html', context)


@transaction.atomic
def pago_contrareembolso(request):
    """
    Procesa la solicitud de pago contrareembolso, crea el pedido final en DB, 
    envía el email en un hilo y limpia la sesión.
    """ 

    # 1. Asegura que tenemos los datos en la sesión y el carrito no está vacío
    datos_envio = request.session.get('datos_envio_checkout')
    carrito = Carrito(request)
   
    # Si falta la sesión o el carrito está vacío, se retorna al checkout.
    if not datos_envio or len(carrito) == 0:
        messages.error(request, "Faltan datos de envío o el carrito está vacío")
        return redirect('pedidos:checkout')
    
    try:
        # Totales del carrito antes de limpiarlo
        subtotal = carrito.obtener_precio_total()
        envio = carrito.obtener_coste_envio()
        impuestos = carrito.obtener_impuestos()
        total = carrito.obtener_total_final()
        datos_empresa = DatosEmpresa.get_datos()

        # Crear el Objeto Pedido (Registro definitivo)
        pedido = Pedido.objects.create(
            cliente=request.user if request.user.is_authenticated else None,
            nombre_cliente=datos_envio['nombre'],
            apellidos_cliente=datos_envio['apellidos'],
            email_cliente=datos_envio['email'],
            telefono_cliente=datos_envio['telefono'],
            direccion_envio=datos_envio['direccion'],
            ciudad_envio=datos_envio['ciudad'],
            codigo_postal_envio=datos_envio['codigo_postal'],
            subtotal=subtotal,
            impuestos=impuestos,
            coste_entrega=envio,
            total=total,
            metodo_pago='contrareembolso', 
            estado='pendiente', # Estado inicial para contrareembolso
            notas=datos_envio.get('notas', '') or "Pago Contrareembolso. Pendiente de recepción.", 
        )
        
        # Crear los Items del Pedido y Actualizar Stock (¡Importante la transacción!)
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
            # Actualización de stock
            producto = item['producto']
            producto.stock -= item['cantidad']
            producto.save()

        asunto = f'🎉 Confirmación de Pedido PetJoy #{pedido.numero_pedido} (Contrareembolso)'
        html_content = render_to_string('pedidos/email_confirmacion.html', {
            'pedido': pedido,
            'datos_empresa': datos_empresa,
        })
        
        email_thread = threading.Thread(
            target=send_confirmation_email_async,
            args=[
                asunto, 
                html_content, 
                pedido.email_cliente
            ]
        )
        email_thread.start()
        # ------------------------------------------------------------------

        # Limpiar Carrito y Datos de Sesión
        request.session['pedido_id_confirmacion'] = pedido.id 
        del request.session['datos_envio_checkout']
        carrito.limpiar()

        messages.success(request, f'¡Pedido Contrareembolso realizado! Número: {pedido.numero_pedido}')

        # Redirigir a la página de confirmación final
        return redirect('pedidos:confirmacion', pedido_id=pedido.numero_pedido)

    except Exception as e:
        # Si hay un error, el decorador @transaction.atomic asegura un rollback
        messages.error(request, f"Error al crear el pedido contrareembolso: {e}")
        return redirect('pedidos:checkout')
    

def crear_sesion_stripe(request):
    """Crea la sesión de checkout en Stripe y devuelve la URL para redirigir."""
    carrito = Carrito(request)
    datos_envio = request.session.get('datos_envio_checkout')

    if not datos_envio or len(carrito) == 0:
        return JsonResponse({'error': 'Faltan datos de envío o el carrito está vacío.'}, status=400)

    # El total se calcula en la clase Carrito
    total_cents = int(carrito.obtener_total_final() * 100)
    
    line_items = [{
        'price_data': {
            'currency': 'eur', 
            'product_data': {
                'name': 'Pedido PetJoy',
                'description': f'Compra de {len(carrito)} productos.',
            },
            'unit_amount': total_cents,
        },
        'quantity': 1,
    }]

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            # URLs de redireccionamiento
            success_url=request.build_absolute_uri('/pedidos/pago_exitoso/') + '?session_id={CHECKOUT_SESSION_ID}', 
            cancel_url=request.build_absolute_uri('/pedidos/pago_cancelado/'),
            customer_email=datos_envio['email'],
            metadata={
                'user_id': request.user.id if request.user.is_authenticated else None,
            }
        )
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        messages.error(request, f"Error al iniciar el pago con Stripe: {e}. Inténtalo de nuevo.")
        return redirect('pedidos:checkout')


# FUNCIÓN AUXILIAR: El trabajo pesado del envío de correo
def send_confirmation_email_async(asunto, html_content, email_cliente):
    # Los imports se hacen dentro de la función para mayor seguridad en hilos
    from django.core.mail import send_mail
    from django.conf import settings
    import traceback # Asegúrate de que traceback esté disponible

    try:
        send_mail(
            asunto,
            '', 
            settings.DEFAULT_FROM_EMAIL,
            [email_cliente],
            html_message=html_content,
            fail_silently=False # Fuerza la excepción
        )
        print(f"CORREO ENVIADO EXITOSAMENTE a {email_cliente}") 

    except Exception as e:
        # ESTE ES EL CÓDIGO QUE NECESITA EJECUTARSE
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR CRÍTICO AL ENVIAR CORREO ASÍNCRONO a {email_cliente}: {e}")
        traceback.print_exc() # Imprime el stack trace del fallo SMTP
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

@transaction.atomic
def pago_exitoso(request):
    """
    Verifica el pago, crea el pedido final en DB, envía el email y limpia la sesión.
    Usa 'confirmacion.html' y 'email_confirmacion.html'.
    """
    session_id = request.GET.get('session_id')
    datos_envio = request.session.get('datos_envio_checkout')
    
    if not session_id or not datos_envio:
        messages.error(request, "Error de sesión. Vuelve a intentar la compra.")
        return redirect('pedidos:checkout')
        
    try:
        # Verificar la Sesión de Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != "paid":
            return redirect('pedidos:pago_cancelado')

        # Generar el Pedido 
        carrito = Carrito(request)
        datos_empresa = DatosEmpresa.get_datos()
        
        if len(carrito) == 0:
             messages.info(request, "El pedido ya fue procesado. Revisa tu correo.")
             return redirect('pedidos:seguimiento')

        subtotal = carrito.obtener_precio_total()
        envio = carrito.obtener_coste_envio()
        impuestos = carrito.obtener_impuestos()
        total = carrito.obtener_total_final()
        
        # Crear el Objeto Pedido (Registro definitivo)
        pedido = Pedido.objects.create(
            cliente=request.user if request.user.is_authenticated else None,
            nombre_cliente=datos_envio['nombre'],
            apellidos_cliente=datos_envio['apellidos'],
            email_cliente=datos_envio['email'],
            telefono_cliente=datos_envio['telefono'],
            direccion_envio=datos_envio['direccion'],
            ciudad_envio=datos_envio['ciudad'],
            codigo_postal_envio=datos_envio['codigo_postal'],
            subtotal=subtotal,
            impuestos=impuestos,
            coste_entrega=envio,
            total=total,
            metodo_pago='tarjeta', 
            estado='procesando', 
            notas=f"Stripe Session ID: {session_id}",
        )
        
        # Crear los Items del Pedido y Actualizar Stock
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
            producto = item['producto']
            producto.stock -= item['cantidad']
            producto.save()
            
        # Enviar Email de Confirmación
        asunto = f'🎉 Confirmación de Pedido PetJoy #{pedido.numero_pedido}'
        html_content = render_to_string('pedidos/email_confirmacion.html', {
            'pedido': pedido,
            'datos_empresa': datos_empresa,
        })
        email_thread = threading.Thread(
            target=send_confirmation_email_async,
            args=[
                asunto, 
                html_content, 
                pedido.email_cliente
            ]
        )
        email_thread.start()
        # Limpiar Carrito y Datos de Sesión
        request.session['pedido_id_confirmacion'] = pedido.id 
        del request.session['datos_envio_checkout']
        carrito.limpiar()
        
        messages.success(request, f'¡Pedido realizado con éxito! Número de pedido: {pedido.numero_pedido}')
        
        # Redirigir a la página de confirmación final
        return redirect('pedidos:confirmacion', pedido_id=pedido.numero_pedido)

    except stripe.error.InvalidRequestError as e:
        messages.error(request, f"Error de Stripe: {e}. El pago no pudo ser verificado.")
        return redirect('pedidos:checkout')
    except Exception as e:
        messages.error(request, f"Error inesperado durante la confirmación: {e}")
        return redirect('pedidos:checkout')

def pago_cancelado(request):
    """Muestra una página informando que el pago ha sido cancelado."""
    return render(request, 'pedidos/pago_cancelado.html')

def confirmacion_pedido(request, pedido_id):
    """Página de confirmación del pedido. Obtiene el pedido ID de la sesión."""

    pedido = get_object_or_404(Pedido, numero_pedido=pedido_id)
    datos_empresa = DatosEmpresa.get_datos()
    
    # Limpia la referencia al ID para prevenir que la página se recargue y muestre el mismo pedido
    request.session.pop('pedido_id_confirmacion', None) 
    
    context = {
        'pedido': pedido,
        'datos_empresa': datos_empresa,
    }
    return render(request, 'pedidos/confirmacion.html', context)

def seguimiento_pedido(request):
    """
    Maneja el seguimiento de un pedido, permitiendo la búsqueda automática 
    o la búsqueda manual.
    """
    pedido = None
    
    if request.method == 'POST':
        numero_pedido = request.POST.get('numero_pedido')
        email = request.POST.get('email')
        
        if not email and request.user.is_authenticated:
            email = request.user.email

        try:
            pedido = Pedido.objects.get(numero_pedido=numero_pedido, email_cliente=email)
            messages.success(request, f"Detalles del Pedido #{numero_pedido} encontrados.")
            
        except Pedido.DoesNotExist:
            messages.error(request, 'No se encontró el pedido con esos datos. Inténtalo de nuevo.')
    
    else:
        numero_pedido_get = request.GET.get('numero_pedido')
        
        if request.user.is_authenticated and numero_pedido_get:
            try:
                pedido = Pedido.objects.get(numero_pedido=numero_pedido_get, cliente=request.user)
                messages.info(request, f"Mostrando seguimiento del Pedido #{numero_pedido_get}.")
                
            except Pedido.DoesNotExist:
                messages.error(request, 'No se encontró un pedido asociado a tu cuenta con ese número.')

    context = {
        'pedido': pedido,
        'numero_pedido_precargado': request.GET.get('numero_pedido', '') 
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
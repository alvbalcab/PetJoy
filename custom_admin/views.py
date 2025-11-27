"""Vistas del panel administrativo personalizado.

Contiene vistas protegidas con `staff_member_required` para gestionar
productos y pedidos desde una interfaz propia en `custom_admin`.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from productos.models import Producto, ImagenProducto
from pedidos.models import Pedido
from .forms import ProductoForm, EstadoPedidoForm


@staff_member_required(login_url='clientes:login')
def admin_dashboard(request):
    """Muestra el tablero con métricas rápidas (pedidos, productos agotados)."""
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_procesando = Pedido.objects.filter(estado='procesando').count()
    productos_agotados = Producto.objects.filter(stock=0).count()
    ultimos_pedidos = Pedido.objects.all().order_by('-fecha_creacion')[:5]

    context = {
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_procesando': pedidos_procesando,
        'productos_agotados': productos_agotados,
        'ultimos_pedidos': ultimos_pedidos,
    }
    return render(request, 'custom_admin/dashboard.html', context)


@staff_member_required(login_url='clientes:login')
def lista_productos(request):
    """Lista los productos para gestión desde el panel."""
    productos = Producto.objects.all().order_by('-id')
    return render(request, 'custom_admin/productos/lista.html', {'productos': productos})


@staff_member_required(login_url='clientes:login')
def crear_producto(request):
    """Crear un nuevo `Producto` desde el panel personalizado."""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()

            imagen = request.FILES.get('imagen_principal')
            if imagen:
                ImagenProducto.objects.create(producto=producto, imagen=imagen, es_principal=True)

            messages.success(request, 'Producto creado correctamente.')
            return redirect('custom_admin:lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'custom_admin/productos/formulario.html', {'form': form, 'titulo': 'Crear Producto'})


@staff_member_required(login_url='clientes:login')
def editar_producto(request, producto_id):
    """Editar un `Producto` existente identificado por `producto_id`."""
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()

            imagen = request.FILES.get('imagen_principal')
            if imagen:
                ImagenProducto.objects.filter(producto=producto).delete()
                ImagenProducto.objects.create(producto=producto, imagen=imagen, es_principal=True)

            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('custom_admin:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'custom_admin/productos/formulario.html', {'form': form, 'titulo': 'Editar Producto'})


@staff_member_required(login_url='clientes:login')
def eliminar_producto(request, producto_id):
    """Eliminar un `Producto` por su id."""
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado.')
    return redirect('custom_admin:lista_productos')


@staff_member_required(login_url='clientes:login')
def lista_pedidos(request):
    """Lista todos los pedidos para gestión administrativa."""
    pedidos = Pedido.objects.all().order_by('-fecha_creacion')
    return render(request, 'custom_admin/pedidos/lista.html', {'pedidos': pedidos})


@staff_member_required(login_url='clientes:login')
def detalle_pedido_admin(request, pedido_id):
    """Detalle y edición rápida del estado de un `Pedido`."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = EstadoPedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estado actualizado a {pedido.get_estado_display()}.')
            return redirect('custom_admin:detalle_pedido', pedido_id=pedido.id)
    else:
        form = EstadoPedidoForm(instance=pedido)
    return render(request, 'custom_admin/pedidos/detalle.html', {'pedido': pedido, 'form': form})
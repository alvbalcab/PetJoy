from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Producto, Categoria, Marca


def catalogo_productos(request):
    """Vista del catálogo de productos con filtros"""
    
    productos = Producto.objects.filter(esta_disponible=True)
        
    # 1. Filtro por categoría
    categoria_id_str = request.GET.get('categoria') # Capturamos como string
    if categoria_id_str:
        productos = productos.filter(categoria_id=categoria_id_str)
    
    # 2. Filtro por marca
    marca_id_str = request.GET.get('marca') # Capturamos como string
    if marca_id_str:
        productos = productos.filter(marca_id=marca_id_str)
    
    # 3. Filtro por género
    genero = request.GET.get('genero')
    if genero:
        productos = productos.filter(genero=genero)
    
    # 4. Búsqueda
    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(marca__nombre__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(productos, 12)
    page = request.GET.get('page')
    productos_paginados = paginator.get_page(page)
        
    # Convertimos los strings de ID a enteros para que coincidan con la lógica del HTML
    try:
        categoria_seleccionada_id = int(categoria_id_str)
    except (ValueError, TypeError):
        categoria_seleccionada_id = None
        
    try:
        marca_seleccionada_id = int(marca_id_str)
    except (ValueError, TypeError):
        marca_seleccionada_id = None
    
    context = {
        'productos': productos_paginados,
        'categorias': Categoria.objects.all(),
        'marcas': Marca.objects.all(),
        'query': query,
        # Variables clave para el resaltado del sidebar
        'categoria_seleccionada_id': categoria_seleccionada_id,
        'marca_seleccionada_id': marca_seleccionada_id,
    }
    return render(request, 'productos/catalogo.html', context)


def detalle_producto(request, slug):
    """Vista de detalle de un producto"""
    producto = get_object_or_404(Producto, slug=slug, esta_disponible=True)
    
    # Productos relacionados
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        esta_disponible=True
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'productos/detalle.html', context)


def productos_por_categoria(request, categoria_id):
    """Vista de productos por categoría"""
    # Nota: Esta vista es redundante si se usa catalogo_productos con filtros,
    # pero la mantenemos si tu urls.py la requiere.
    categoria = get_object_or_404(Categoria, id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria, esta_disponible=True)
    
    # Paginación
    paginator = Paginator(productos, 12)
    page = request.GET.get('page')
    productos_paginados = paginator.get_page(page)
    
    context = {
        'categoria': categoria,
        'productos': productos_paginados,
        'categorias': Categoria.objects.all(),
        'categoria_seleccionada_id': categoria.id, # Añadido para consistencia si se usa esta vista
    }
    return render(request, 'productos/por_categoria.html', context)
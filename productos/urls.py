from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.catalogo_productos, name='catalogo'),
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='por_categoria'),
]

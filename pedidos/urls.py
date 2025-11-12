from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('crear_sesion_stripe/', views.crear_sesion_stripe, name='crear_sesion_stripe'),
    path('pago_exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago_cancelado/', views.pago_cancelado, name='pago_cancelado'),
    path('confirmacion/<str:pedido_id>/', views.confirmacion_pedido, name='confirmacion'),
    path('seguimiento/', views.seguimiento_pedido, name='seguimiento'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
]

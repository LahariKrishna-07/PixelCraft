from django.urls import path
from django.conf import settings          # <--- THIS IS THE FIX
from django.conf.urls.static import static
from . import views
from .views import *

urlpatterns = [
    path('', views.components_list, name='components_list'),
    path('component/<int:pk>/', views.component_detail, name='component_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:inventory_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('my-orders/', views.order_history, name='order_history'),
    path('my-orders/delivered/<int:item_id>/', views.mark_as_delivered, name='mark_as_delivered'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
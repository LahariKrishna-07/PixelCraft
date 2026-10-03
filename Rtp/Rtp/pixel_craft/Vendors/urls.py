from django.urls import path
from .views import (
    Home_page, Dashboard, Vendor_profile_edit, Profile, 
    Vendors_Inventory, add_product, edit_inventory_item, 
    delete_inventory_item, vendor_orders_view,vendor_analytics
)

urlpatterns = [
    path('', Home_page, name='Vendors_Home'),
    path('Vendors_dashboard', Dashboard, name='vendor_dashboard'),
    path('Vendor_inventory', Vendors_Inventory, name='vendor_inventory'),
    
    # <--- UPDATED THIS LINE --->
    path('Vendor_orders', vendor_orders_view, name='vendor_orders'), 
    
    path('Vendor_analytics', vendor_analytics, name='vendor_analytics'),
    path('Vendor_search', Dashboard, name='vendor_search'),
    path('Vendor_notifications', Dashboard, name='vendor_notifications'),
    path('Vendor_settings', Dashboard, name='vendor_settings'),
    path('Vendor_payouts', Dashboard, name='vendor_payouts'),
    path('Vendor_profile_edit', Vendor_profile_edit, name='vendor_profile_edit'),
    path('Vendor_profile', Profile, name='vendor_profile'),
    path('add_product', add_product, name='add_product'),
    path('inventory/edit/<int:item_id>/', edit_inventory_item, name='edit_inventory_item'),
    path('inventory/delete/<int:item_id>/', delete_inventory_item, name='delete_inventory_item'),
]
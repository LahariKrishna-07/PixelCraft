from django.shortcuts import render
from django.http import HttpResponse
from .models import Vendor
from .forms import VendorProfileEditForm
from Accounts.decorators import ordinary_user_required
from django.contrib.auth.decorators import login_required
from .forms import InventoryItemForm, AddComponentFullForm
# Create your views here.
def Home_page(req):
    return render(req,'Vendors/Home.html',{})
def Dashboard(req):
    return HttpResponse("Dashboard")
def Vendor_profile_edit(req):
    if req.method=='POST':
        model=VendorProfileEditForm(req.POST,req.FILES,instance=req.user.vendor)
        if model.is_valid():
            model.save()
    else:
        model=VendorProfileEditForm(instance=req.user.vendor)
    return render(req,'Vendors/Vendor_Profile_Edit.html',{'form':model})
def Profile(req):
    return render(req,'Vendors/Vendor_Profile.html',{'vendor':req.user.vendor})
@login_required
def Vendors_Inventory(request):
    vendor_items = request.user.vendor.inventory.all().order_by('-created_at')
    return render(request, 'Vendors/Vendor_Inventory.html', {'inventory': vendor_items})


""""Gemini"""
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Components, InventoryItem
from .forms import AddComponentFullForm
# Ensure you import your vendor_required decorator here!
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor, InventoryItem
from pc_build.models import Components, Socket, MemoryGeneration, CPUSpec, MotherboardSpec, RAMSpec # Make sure these are imported
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor, InventoryItem
# Make sure to import ALL the new spec models!
from pc_build.models import (
    Components, Socket, MemoryGeneration, 
    CPUSpec, MotherboardSpec, RAMSpec, 
    PSUSpec, CoolerSpec, CaseSpec, GPUSpec, StorageSpec
)

@login_required
def add_product(request):
    try:
        vendor = request.user.vendor
    except:
        messages.error(request, "You need a vendor account to add products.")
        return redirect('Vendors_Home')

    all_components = Components.objects.all().order_by('category', 'name')

    if request.method == 'POST':
        component_mode = request.POST.get('component_mode')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')

        if component_mode == 'existing':
            component_id = request.POST.get('component_id')
            component = Components.objects.get(id=component_id)
        
        elif component_mode == 'new':
            new_category = request.POST.get('new_category')
            component = Components.objects.create(
                name=request.POST.get('new_name'),
                category=new_category,
                brand=request.POST.get('new_brand', 'Generic'),
                description=request.POST.get('new_description', ''),
                specs=request.POST.get('new_specs', ''),
                image=request.FILES.get('new_image')
            )

            # --- DYNAMIC SPECIFICATION ROUTING ---
            
            if new_category == 'CPU':
                socket_name = request.POST.get('new_socket') 
                socket_obj, _ = Socket.objects.get_or_create(name=socket_name)
                
                cpu_spec = CPUSpec.objects.create(
                    component=component,
                    socket=socket_obj,
                    tdp_watts=int(request.POST.get('new_cpu_tdp', 65))
                )
                
                mem_gens = request.POST.getlist('new_memory_gens') 
                for mem_name in mem_gens:
                    mem_obj, _ = MemoryGeneration.objects.get_or_create(name=mem_name)
                    cpu_spec.supported_memory.add(mem_obj)

            elif new_category == 'Motherboard':
                socket_name = request.POST.get('new_socket')
                socket_obj, _ = Socket.objects.get_or_create(name=socket_name)
                
                mem_name = request.POST.get('new_memory_gen')
                mem_obj, _ = MemoryGeneration.objects.get_or_create(name=mem_name)
                
                MotherboardSpec.objects.create(
                    component=component,
                    socket=socket_obj,
                    form_factor=request.POST.get('new_form_factor'),
                    memory_generation=mem_obj
                )

            elif new_category == 'RAM':
                mem_name = request.POST.get('new_memory_gen')
                mem_obj, _ = MemoryGeneration.objects.get_or_create(name=mem_name)
                
                RAMSpec.objects.create(
                    component=component,
                    generation=mem_obj,
                    speed_mhz=int(request.POST.get('new_ram_speed', 0))
                )
                
            elif new_category == 'PSU':
                PSUSpec.objects.create(
                    component=component,
                    wattage=int(request.POST.get('new_psu_wattage', 0)),
                    efficiency=request.POST.get('new_psu_efficiency', ''),
                    is_modular=(request.POST.get('new_psu_modular') == 'True')
                )
                
            elif new_category == 'Cooling':
                is_liquid = request.POST.get('new_cooler_liquid') == 'True'
                rad_size = request.POST.get('new_cooler_rad_size')
                # Only save rad_size if it's liquid cooling and a number was provided
                rad_size = int(rad_size) if is_liquid and rad_size else None
                
                cooler_spec = CoolerSpec.objects.create(
                    component=component,
                    is_liquid_cooler=is_liquid,
                    radiator_size_mm=rad_size
                )
                
                # Handle comma-separated sockets (e.g., "AM4, AM5, LGA 1700")
                sockets_str = request.POST.get('new_cooler_sockets', '')
                for s_name in sockets_str.split(','):
                    s_name = s_name.strip()
                    if s_name:
                        socket_obj, _ = Socket.objects.get_or_create(name=s_name)
                        cooler_spec.supported_sockets.add(socket_obj)

            elif new_category == 'Case':
                CaseSpec.objects.create(
                    component=component,
                    max_form_factor=request.POST.get('new_case_form_factor'),
                    max_gpu_length_mm=int(request.POST.get('new_case_gpu_len', 0))
                )

            elif new_category == 'GPU':
                GPUSpec.objects.create(
                    component=component,
                    length_mm=int(request.POST.get('new_gpu_len', 0)),
                    recommended_psu_wattage=int(request.POST.get('new_gpu_psu', 0)),
                    vram_gb=int(request.POST.get('new_gpu_vram', 0)),
                    tdp_watts=int(request.POST.get('new_gpu_tdp', 200))
                )

            elif new_category == 'Storage':
                StorageSpec.objects.create(
                    component=component,
                    drive_type=request.POST.get('new_storage_type'),
                    capacity_gb=int(request.POST.get('new_storage_cap', 0))
                )

        # --- INVENTORY CREATION ---
        inventory_item, created = InventoryItem.objects.get_or_create(
            vendor=vendor,
            component=component,
            defaults={'price': price, 'stock_quantity': stock_quantity}
        )

        if not created:
            inventory_item.price = price
            inventory_item.stock_quantity += int(stock_quantity)
            inventory_item.save()
            messages.success(request, f"Updated your existing stock for {component.name}.")
        else:
            messages.success(request, f"Successfully added {component.name} to your inventory!")

        return redirect('vendor_inventory')

    return render(request, 'Vendors/vendor_add_component.html', {'all_components': all_components})
from django.shortcuts import get_object_or_404
from .models import InventoryItem
from .forms import InventoryItemForm # You can reuse the simple form we made earlier


def edit_inventory_item(request, item_id):
    # Ensure the item exists AND belongs to this vendor
    item = get_object_or_404(InventoryItem, id=item_id, vendor=request.user.vendor)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {item.component.name} successfully!")
            return redirect('vendor_inventory')
    else:
        form = InventoryItemForm(instance=item)
        
    return render(request, 'Vendors/edit_inventory_item.html', {'form': form, 'item': item})


def delete_inventory_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id, vendor=request.user.vendor)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item removed from your inventory.")
        return redirect('vendor_inventory')
    return render(request, 'Vendors/confirm_delete.html', {'item': item})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor
from pc_build.models import OrderItem  # Ensure this imports your OrderItem from the pc_build app!

@login_required
def vendor_orders_view(request):
    try:
        # Get the vendor profile linked to the logged-in user
        my_vendor_profile = request.user.vendor
    except Vendor.DoesNotExist:
        messages.error(request, "You do not have a registered vendor account.")
        return redirect('Vendors_Home')

    # Handle the "Mark as Shipped" button click
    if request.method == 'POST':
        order_item_id = request.POST.get('order_item_id')
        if order_item_id:
            # Find the specific item and ensure it belongs to this vendor
            item_to_update = OrderItem.objects.get(id=order_item_id, vendor=my_vendor_profile)
            item_to_update.vendor_status = 'Shipped'
            item_to_update.save()
            messages.success(request, f"Order #{item_to_update.order.id} marked as Shipped!")
            return redirect('vendor_orders')

    # Fetch Pending Orders (Needs to be shipped)
    pending_orders = OrderItem.objects.filter(
        vendor=my_vendor_profile, 
        vendor_status='Pending'
    ).order_by('-order__created_at')

    # Fetch Shipped/Completed Orders (History)
    shipped_orders = OrderItem.objects.filter(
        vendor=my_vendor_profile, 
        vendor_status__in=['Shipped', 'Delivered']
    ).order_by('-order__created_at')

    return render(request, 'Vendors/vendor_orders.html', {
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders
    })
# Make sure these imports are at the top of your file!
from .models import Vendor, InventoryItem, Components  # Keeps your Vendor imports safe
from pc_build.models import Order, OrderItem           # Pulls the Orders from the pc_build app!
from Vendors.models import Vendor

# --- Paste this at the bottom of pc_build/views.py ---

@login_required
def checkout_view(request):
    """Handles the checkout process and explodes hybrid builds into individual vendor orders."""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    if request.method == 'POST':
        cart_total = sum(item.item_total for item in cart_items)
        
        # Create the Main Order
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name', request.user.username),
            shipping_address=request.POST.get('shipping_address', 'Address provided at checkout'),
            total_amount=cart_total
        )
        
        # Loop through Cart and "Flatten" into OrderItems
        for cart_item in cart_items:
            if cart_item.inventory_item:
                # Single Item
                OrderItem.objects.create(
                    order=order,
                    vendor=cart_item.inventory_item.vendor,
                    inventory_item=cart_item.inventory_item,
                    price_at_purchase=cart_item.inventory_item.price,
                    quantity=cart_item.quantity
                )
                cart_item.inventory_item.stock_quantity -= cart_item.quantity
                cart_item.inventory_item.save()
                
            elif cart_item.custom_build:
                # Hybrid Build
                for build_item in cart_item.custom_build.items.all():
                    OrderItem.objects.create(
                        order=order,
                        vendor=build_item.inventory_item.vendor,
                        inventory_item=build_item.inventory_item,
                        price_at_purchase=build_item.inventory_item.price,
                        quantity=cart_item.quantity
                    )
                    build_item.inventory_item.stock_quantity -= cart_item.quantity
                    build_item.inventory_item.save()
        
        # Empty the Cart
        cart_items.delete()
        messages.success(request, f"Order #{order.id} placed successfully! Vendors have been notified.")
        return redirect('order_history')

    return render(request, 'pc_build/checkout.html', {'cart_items': cart_items})

@login_required
def order_history(request):
    """Customer View: Shows all orders placed by this user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items__inventory_item__component')
    return render(request, 'pc_build/order_history.html', {'orders': orders})
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from pc_build.models import OrderItem, Order
@login_required
def Dashboard(request):
    vendor = request.user.vendor
    # Focus on things that need ACTION
    pending_items = OrderItem.objects.filter(vendor=vendor, vendor_status='Pending')
    low_stock = vendor.inventory.filter(stock_quantity__lt=5) # Alert if stock is less than 5
    
    return render(request, 'Vendors/dashboard.html', {
        'pending_items': pending_items,
        'low_stock': low_stock,
    })
import json
from django.db.models.functions import TruncDate
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from pc_build.models import OrderItem # Adjust if your app name is different

@login_required
def vendor_analytics(request):
    try:
        vendor = request.user.vendor
    except:
        messages.error(request, "You do not have a vendor account.")
        return redirect('Vendors_Home')

    last_30_days = timezone.now() - timedelta(days=30)
    
    # Base query for delivered/shipped items in the last 30 days
    delivered_items = OrderItem.objects.filter(
        vendor=vendor, 
        vendor_status__in=['Shipped', 'Delivered'],
        order__created_at__gte=last_30_days
    )

    # 1. Dashboard Stats (Fully Dynamic)
    revenue_data = delivered_items.aggregate(Sum('price_at_purchase'))
    monthly_revenue = revenue_data['price_at_purchase__sum'] or 0

    total_orders = delivered_items.values('order').distinct().count()
    total_units = delivered_items.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # 2. Top Selling (for the Table & Cards)
    top_selling = delivered_items.values('inventory_item__component__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    best_seller = top_selling.first() if top_selling else None

    # 3. Line Chart (Revenue over time)
    daily_revenue = delivered_items.annotate(
        date=TruncDate('order__created_at')
    ).values('date').annotate(
        daily_total=Sum('price_at_purchase')
    ).order_by('date')

    rev_labels = [item['date'].strftime('%b %d') for item in daily_revenue]
    rev_data = [float(item['daily_total']) for item in daily_revenue]

    # 4. Pie Chart (Category mix)
    category_sales = delivered_items.values('inventory_item__component__category').annotate(
        total=Sum('quantity')
    ).order_by('-total')

    cat_labels = [item['inventory_item__component__category'] for item in category_sales]
    cat_data = [item['total'] for item in category_sales]

    # 5. Detailed Export Data (CSV Spreadsheet)
    transactions = delivered_items.values(
        'order__id',
        'inventory_item__component__name',
        'inventory_item__component__category',
        'price_at_purchase',
        'quantity',
        'order__created_at'
    ).order_by('-order__created_at')

    export_data = [
        {
            'order_id': t['order__id'],
            'component': t['inventory_item__component__name'],
            'category': t['inventory_item__component__category'],
            'price': float(t['price_at_purchase']),
            'qty': t['quantity'],
            'date': t['order__created_at'].strftime('%Y-%m-%d %H:%M')
        } for t in transactions
    ]

    return render(request, 'Vendors/analytics.html', {
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'total_units': total_units,
        'top_selling': top_selling,
        'best_seller': best_seller,
        'rev_labels': json.dumps(rev_labels),
        'rev_data': json.dumps(rev_data),
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        'export_data': json.dumps(export_data),
    })
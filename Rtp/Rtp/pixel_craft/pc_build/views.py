from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Imports from your pc_build models
from .models import CartItem, CustomBuild, Order, OrderItem

# Imports from your Vendors models
from Vendors.models import InventoryItem, Components
from django.db.models import Q, Min
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from pc_build.models import Components # Adjust this import to match your app name

from django.db.models import Min, Q
# Ensure you import your Component model

@login_required
def components_list(request):
    """Shows all hardware in the catalog with Search, Filter, Sort, and Specs."""
    
    # 1. Annotate price AND fetch all related specs in a single query for speed
    components = Components.objects.annotate(
        lowest_price=Min('vendor_listings__price') # Keep your existing relation name here!
    ).select_related(
        'cpu_spec', 'cpu_spec__socket',
        'gpu_spec',
        'motherboard_spec', 'motherboard_spec__socket', 'motherboard_spec__memory_generation',
        'ram_spec', 'ram_spec__generation',
        'psu_spec', 'case_spec', 'cooler_spec', 'storage_spec'
    )

    # 2. Handle Search Query
    query = request.GET.get('q')
    if query:
        components = components.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query) |
            Q(description__icontains=query)
        )

    # 3. Handle Category Filter
    category = request.GET.get('category')
    if category:
        components = components.filter(category=category)

    # 4. Handle Price Range
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    
    if min_price:
        components = components.filter(lowest_price__gte=min_price)
    if max_price:
        components = components.filter(lowest_price__lte=max_price)

    # 5. Handle Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        components = components.order_by('lowest_price')
    elif sort_by == 'price_desc':
        components = components.order_by('-lowest_price')
    elif sort_by == 'name_desc':
        components = components.order_by('-name')
    else:
        components = components.order_by('name')

    return render(request, 'pc_build/components_list.html', {
        'components': components,
    })
@login_required
def component_detail(request, pk):
    """Shows details for a specific component and all vendors selling it."""
    component = get_object_or_404(Components, pk=pk)
    
    # Fetch all active vendor offers for this specific part, cheapest first
    vendor_offers = InventoryItem.objects.filter(
        component=component,
        is_active=True,
        stock_quantity__gt=0
    ).order_by('price')
    
    return render(request, 'pc_build/component_detail.html', {
        'component': component,
        'vendor_offers': vendor_offers
    })

# ---------------------------------------------------------
# CART VIEWS
# ---------------------------------------------------------

@login_required
def add_to_cart(request, inventory_id):
    """Adds a single vendor component to the cart."""
    inventory_item = get_object_or_404(InventoryItem, id=inventory_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        inventory_item=inventory_item,
        custom_build=None 
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Updated quantity of {inventory_item.component.name} in your cart.")
    else:
        messages.success(request, f"Added {inventory_item.component.name} to your cart.")
        
    return redirect('cart_view')

@login_required
def remove_from_cart(request, cart_item_id):
    """Removes an item or build from the cart."""
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.warning(request, "Item removed from cart.")
    return redirect('cart_view')

@login_required
def cart_view(request):
    """Displays the user's shopping cart."""
    cart_items = CartItem.objects.filter(user=request.user).order_by('-added_at')
    cart_total = sum(item.item_total for item in cart_items)
    
    return render(request, 'pc_build/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

# ---------------------------------------------------------
# CHECKOUT & ORDER VIEWS
# ---------------------------------------------------------

@login_required
def checkout_view(request):
    """Handles checkout and explodes hybrid builds into individual vendor orders."""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    if request.method == 'POST':
        cart_total = sum(item.item_total for item in cart_items)
        
        # 1. Create the Main Order
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name', request.user.username),
            shipping_address=request.POST.get('shipping_address', 'Address provided at checkout'),
            total_amount=cart_total
        )
        
        # 2. Loop through Cart and "Flatten" into OrderItems
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
        
        # 3. Empty the Cart
        cart_items.delete()
        messages.success(request, f"Order #{order.id} placed successfully! Vendors have been notified.")
        return redirect('order_history')

    return render(request, 'pc_build/checkout.html', {'cart_items': cart_items})

@login_required
def order_history(request):
    """Customer View: Shows all historical orders placed by this user node."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related(
        'items__inventory_item__component'
    )
    return render(request, 'pc_build/order_history.html', {'orders': orders})
@login_required
def mark_as_delivered(request, item_id):
    """Allows the customer to confirm they received a specific shipped item."""
    if request.method == 'POST':
        # Find the specific item, but ONLY if it belongs to an order owned by this user
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        
        # Only update it if it's currently marked as Shipped
        if item.vendor_status == 'Shipped':
            item.vendor_status = 'Delivered'
            item.save()
            messages.success(request, f"Awesome! {item.inventory_item.component.name} marked as Delivered.")
            
            # SMART LOGIC: Check if the entire Master Order is fully delivered now
            main_order = item.order
            # If there are NO items left in this order that aren't "Delivered"...
            if not main_order.items.exclude(vendor_status='Delivered').exists():
                main_order.status = 'Completed'
                main_order.save()
                messages.success(request, f"Order #{main_order.id} is now fully completed!")
                
    return redirect('order_history')

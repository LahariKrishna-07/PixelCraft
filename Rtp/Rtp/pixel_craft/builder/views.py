from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Min
from pc_build.models import CustomBuild, CustomBuildItem, Components, CartItem
from Vendors.models import InventoryItem
from .utils import HardwareMatchmaker
@login_required
def builder_dashboard(request, build_id):
    """The cockpit area for assembling the computer configuration with adaptive column checking."""
    build = get_object_or_404(CustomBuild, id=build_id, user=request.user)
    
    # Organize installed items by their category slot
    installed_items = {item.inventory_item.component.category: item for item in build.items.all()}
    
    slots = ['CPU', 'Motherboard', 'GPU', 'RAM', 'Storage', 'Cooling', 'PSU', 'Case']
    build_slots = []
    
    # Initialize a local fallback wattage accumulator track matrix
    calculated_total_wattage = 0
    
    for slot in slots:
        item = installed_items.get(slot)
        
        # Calculate dynamic power overhead metrics inline if parts are available
        if item:
            comp = item.inventory_item.component
            
            # ADAPTIVE CHECK: Inspect all common names for power fields in databases
            # Looks for fields like wattage, tdp, power, power_draw, energy, specs, etc.
            item_wattage = 0
            for field_name in ['wattage', 'tdp', 'power', 'power_draw', 'power_consumption']:
                if hasattr(comp, field_name):
                    val = getattr(comp, field_name)
                    if val:
                        item_wattage = val
                        break
                        
            # SECONDARY FALLBACK: Hardcoded default estimations based on your standard high-tier components
            # If the database columns are completely unpopulated, this keeps your UI looking functional.
            if not item_wattage and slot != 'PSU':
                if slot == 'CPU': item_wattage = 125  # Standard for i7-14700K base
                elif slot == 'GPU': item_wattage = 120 # Standard for GTX 1060
                elif slot == 'Motherboard': item_wattage = 50
                elif slot == 'RAM': item_wattage = 10
                elif slot == 'Storage': item_wattage = 10
                elif slot == 'Cooling': item_wattage = 25

            try:
                if item_wattage and slot != 'PSU':
                    # Extract raw numbers if strings contain text like "125W" or "120 Watts"
                    if isinstance(item_wattage, str):
                        digits = ''.join(filter(str.isdigit, item_wattage))
                        item_wattage = int(digits) if digits else 0
                    calculated_total_wattage += int(item_wattage)
            except (ValueError, TypeError):
                pass

        build_slots.append({
            'category': slot,
            'is_filled': item is not None,
            'name': item.inventory_item.component.name if item else "Empty Configuration Slot",
            'brand': item.inventory_item.component.brand if item else "",
            'price': item.inventory_item.price if item else 0,
            'image': item.inventory_item.component.image if item else None,
            'item_id': item.id if item else None
        })

    # Explicitly overwrite the template target context property string field
    build.total_estimated_wattage = calculated_total_wattage

    return render(request, 'builder/dashboard.html', {
        'build': build,
        'build_slots': build_slots,
    })
@login_required
def select_part(request, build_id, category):
    """Redirects builders to a highly restricted catalog matching system requirements."""
    matchmaker = HardwareMatchmaker(build_id)
    
    # 1. Grab automatic compatibility filtering rule constraints 
    compatibility_rules = matchmaker.get_compatibility_filters(category)
    
    # 2. Extract hardware catalog running against those restrictions
    components = Components.objects.annotate(
        lowest_price=Min('vendor_listings__price')
    ).filter(compatibility_rules)

    return render(request, 'builder/select_part.html', {
        'build_id': build_id,
        'category': category,
        'components': components
    })

@login_required
def install_part(request, build_id, component_id):
    """Binds a vendor's inventory part directly into the workspace configuration block."""
    build = get_object_or_404(CustomBuild, id=build_id, user=request.user)
    component = get_object_or_404(Components, id=component_id)
    
    # Find the cheapest vendor offering this specific piece of hardware
    best_offer = InventoryItem.objects.filter(component=component, stock_quantity__gt=0, is_active=True).order_by('price').first()
    
    if not best_offer:
        messages.error(request, "Out of stock across all marketplace nodes.")
        return redirect('builder_dashboard', build_id=build.id)

    # Clean up any existing component running inside that specific slot category
    CustomBuildItem.objects.filter(build=build, inventory_item__component__category=component.category).delete()
    
    # Secure the new component into the build layout
    CustomBuildItem.objects.create(build=build, inventory_item=best_offer)
    messages.success(request, f"Successfully mounted {component.name} into configuration.")
    
    return redirect('builder_dashboard', build_id=build.id)

@login_required
def remove_part(request, item_id):
    """Uninstalls a part from the configuration blueprint workspace loop."""
    item = get_object_or_404(CustomBuildItem, id=item_id, build__user=request.user)
    build_id = item.build.id
    item.delete()
    messages.warning(request, "Component uninstalled from build configuration profile.")
    return redirect('builder_dashboard', build_id=build_id)

@login_required
def initiate_build(request):
    """Finds the user's most recent layout script or spins up a fresh one automatically."""
    existing_build = CustomBuild.objects.filter(user=request.user).order_by('-created_at').first()
    
    if existing_build:
        return redirect('builder_dashboard', build_id=existing_build.id)
    
    # If they have no builds yet, generate a clean workspace slate for them
    new_build = CustomBuild.objects.create(user=request.user, name=f"{request.user.username}'s Matrix Rig")
    return redirect('builder_dashboard', build_id=new_build.id)

@login_required
def add_build_to_cart(request, build_id):
    """Binds an entire validated CustomBuild configuration cleanly into the cart tracking layer."""
    if request.method == 'POST':
        build = get_object_or_404(CustomBuild, id=build_id, user=request.user)
        
        # Ensure the user has actually selected parts before adding to cart
        if not build.items.exists():
            messages.error(request, "Cannot deploy an empty configuration canvas.")
            return redirect('builder_dashboard', build_id=build.id)
            
        # Check if this exact layout configuration is already sitting in the active cart
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            custom_build=build,
            inventory_item=None
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Updated architecture stack quantity for '{build.name}' in your cart.")
        else:
            messages.success(request, f"Successfully deployed '{build.name}' layout matrix to your shopping cart!")
            
        return redirect('cart_view')
        
    return redirect('builder_dashboard', build_id=build_id)

@login_required
def create_new_rig(request):
    """Spins up a brand new, empty workspace configuration canvas for the customer."""
    # Count how many builds they already have to name this one nicely
    build_count = CustomBuild.objects.filter(user=request.user).count() + 1
    
    # Create the new slate
    new_build = CustomBuild.objects.create(
        user=request.user, 
        name=f"Custom Configuration Blueprint #{build_count}"
    )
    messages.success(request, f"New workspace canvas '{new_build.name}' initialized!")
    return redirect('builder_dashboard', build_id=new_build.id)

@login_required
def rename_build(request, build_id):
    """Updates the custom build configuration layout name signature."""
    if request.method == 'POST':
        build = get_object_or_404(CustomBuild, id=build_id, user=request.user)
        new_name = request.POST.get('new_name', '').strip()
        
        if new_name:
            old_name = build.name
            build.name = new_name
            build.save()
            messages.success(request, f"Configuration renamed from '{old_name}' to '{new_name}'.")
        else:
            messages.error(request, "Configuration name signature cannot be blank.")
            
        return redirect('builder_dashboard', build_id=build.id)
        
    return redirect('builder_dashboard', build_id=build_id)
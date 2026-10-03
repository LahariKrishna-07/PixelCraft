from django.db import models

class Components(models.Model):

    CATEGORY_CHOICES = [
        ('CPU', 'CPU'),
        ('GPU', 'GPU'),
        ('RAM', 'RAM'),
        ('Motherboard', 'Motherboard'),
        ('PSU', 'PSU'),
        ('Storage', 'Storage'),
        ('Case', 'Case'),
        ('Cooler', 'Cooler'),
        ('Monitor', 'Monitor'),
        ('Peripheral', 'Peripheral'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    image = models.ImageField(upload_to='component_images/', blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    specs = models.TextField(blank=True, null=True)

    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
from django.db import models
from django.conf import settings
from Vendors.models import InventoryItem



class CustomBuild(models.Model):
    """The 'Wrapper' for a user's custom PC."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_builds')
    name = models.CharField(max_length=100, default="My Custom PC")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    @property
    def total_build_price(self):
        # Calculates the sum of all parts inside this specific build
        total = sum(item.inventory_item.price for item in self.items.all())
        return total

class CustomBuildItem(models.Model):
    """The specific vendor parts inside the Custom Build."""
    build = models.ForeignKey(CustomBuild, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.inventory_item.component.name} in {self.build.name}"




class CartItem(models.Model):
    """Holds EITHER a single part OR a whole custom build."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    
    # EITHER this is filled out (Normal Item)...
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, null=True, blank=True)
    
    # ...OR this is filled out (Hybrid Pre-build)
    custom_build = models.ForeignKey(CustomBuild, on_delete=models.CASCADE, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.inventory_item:
            return f"Cart: {self.inventory_item.component.name}"
        if self.custom_build:
            return f"Cart: {self.custom_build.name}"
        return "Cart Item"
    
    @property
    def item_total(self):
        # Math gets super easy here!
        if self.inventory_item:
            return self.inventory_item.price * self.quantity
        elif self.custom_build:
            return self.custom_build.total_build_price * self.quantity
        return 0
    
# Add these underneath your Cart models in pc_build/models.py
from Vendors.models import Vendor # Make sure to import your Vendor model

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=255)
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    ITEM_STATUS = (
        ('Pending', 'Pending Vendor Approval'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_orders')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.SET_NULL, null=True)
    
    # We save the price just in case the vendor changes it later!
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    vendor_status = models.CharField(max_length=20, choices=ITEM_STATUS, default='Pending')

    def __str__(self):
        return f"{self.inventory_item.component.name} (Order #{self.order.id})"
# --- 1. Shared Reference Tables ---
class Socket(models.Model):
    name = models.CharField(max_length=20, unique=True) # e.g., "AM5", "LGA 1700"
    def __str__(self): return self.name

class MemoryGeneration(models.Model):
    name = models.CharField(max_length=10, unique=True) # e.g., "DDR4", "DDR5"
    def __str__(self): return self.name


# --- 2. Technical Specification Extensions ---


class MotherboardSpec(models.Model):
    FORM_FACTORS = [
        ('ATX', 'Standard ATX'),
        ('mATX', 'Micro-ATX'),
        ('ITX', 'Mini-ITX'),
        ('E-ATX', 'Extended ATX'),
    ]
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='motherboard_spec')
    socket = models.ForeignKey(Socket, on_delete=models.RESTRICT)
    form_factor = models.CharField(max_length=10, choices=FORM_FACTORS)
    memory_generation = models.ForeignKey(MemoryGeneration, on_delete=models.RESTRICT)

    def __str__(self): return f"Specs for {self.component.name}"

class RAMSpec(models.Model):
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='ram_spec')
    generation = models.ForeignKey(MemoryGeneration, on_delete=models.RESTRICT)
    speed_mhz = models.IntegerField()

    def __str__(self): return f"Specs for {self.component.name}"
# --- Complete the Technical Specification Extensions ---

class PSUSpec(models.Model):
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='psu_spec')
    wattage = models.IntegerField(help_text="e.g., 750, 850, 1000")
    efficiency = models.CharField(max_length=20, help_text="e.g., 80+ Gold, 80+ Bronze")
    is_modular = models.BooleanField(default=True)

    def __str__(self): return f"PSU Specs for {self.component.name}"


class CoolerSpec(models.Model):
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='cooler_spec')
    # A single cooler often comes with multiple brackets to support BOTH Intel and AMD!
    # Therefore, it needs a ManyToMany field to the Socket model.
    supported_sockets = models.ManyToManyField(Socket)
    is_liquid_cooler = models.BooleanField(default=False)
    radiator_size_mm = models.IntegerField(null=True, blank=True, help_text="e.g., 240, 360 (Leave blank for air coolers)")

    def __str__(self): return f"Cooler Specs for {self.component.name}"


class CaseSpec(models.Model):
    # We reuse the Motherboard form factors to map compatibility
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='case_spec')
    max_form_factor = models.CharField(max_length=10, choices=MotherboardSpec.FORM_FACTORS)
    max_gpu_length_mm = models.IntegerField(help_text="Maximum length in mm before the GPU hits the front fans")

    def __str__(self): return f"Case Specs for {self.component.name}"


class CPUSpec(models.Model):
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='cpu_spec')
    socket = models.ForeignKey(Socket, on_delete=models.RESTRICT)
    supported_memory = models.ManyToManyField(MemoryGeneration)
    tdp_watts = models.IntegerField(default=65, help_text="Power consumption in Watts (e.g., 65, 125)") # <-- ADD THIS

class GPUSpec(models.Model):
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='gpu_spec')
    length_mm = models.IntegerField()
    recommended_psu_wattage = models.IntegerField()
    vram_gb = models.IntegerField()
    tdp_watts = models.IntegerField(default=200, help_text="Power consumption in Watts (e.g., 200, 320)") # <-- ADD THIS


class StorageSpec(models.Model):
    TYPE_CHOICES = [
        ('NVMe', 'NVMe M.2'),
        ('SATA_SSD', 'SATA 2.5" SSD'),
        ('HDD', 'SATA 3.5" HDD'),
    ]
    component = models.OneToOneField(Components, on_delete=models.CASCADE, related_name='storage_spec')
    drive_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    capacity_gb = models.IntegerField(help_text="e.g., 1000 for 1TB, 2000 for 2TB")

    def __str__(self): return f"Storage Specs for {self.component.name}"

@property
def total_estimated_wattage(self):
        
    """Iterates through all parts mounted to the current rig array and sums their electrical power draw limits."""
    total = 0
    for item in self.items.all():
            # Check if the hardware model component has a wattage variable attached to it
        component = item.inventory_item.component
            
            # Use safe getattr fallbacks to look for fields like 'wattage', 'tdp', or 'power_draw'
        wattage = getattr(component, 'wattage', getattr(component, 'tdp', 0))
        if wattage:
            try:
                total += int(wattage)
            except (ValueError, TypeError):
                continue
    return total

@property
def is_psu_sufficient(self):
        """Compares system draw metrics against the attached PSU unit limits."""
        # Find if a power supply unit is connected
        psu_item = self.items.filter(inventory_item__component__category__iexact='PSU').first()
        if psu_item:
            psu_capacity = getattr(psu_item.inventory_item.component, 'wattage', 0)
            try:
                return int(psu_capacity) >= self.total_estimated_wattage
            except (ValueError, TypeError):
                pass
        
        # If no PSU is added yet, trigger warning if power draw exceeds standard limits
        return self.total_estimated_wattage < 500
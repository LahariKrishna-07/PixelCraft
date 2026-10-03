from django.contrib import admin
from .models import Components

from .models import *


admin.site.register(CustomBuild)
admin.site.register(CustomBuildItem)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
from django.contrib import admin
from .models import (
    Components, Socket, MemoryGeneration, 
    CPUSpec, MotherboardSpec, RAMSpec, 
    PSUSpec, CoolerSpec, CaseSpec, GPUSpec, StorageSpec
)

# --- Reference Models ---
@admin.register(Socket)
class SocketAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(MemoryGeneration)
class MemoryGenerationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


# --- Master Component Model ---
# (Only add this if you haven't already registered Components)
@admin.register(Components)
class ComponentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'brand')


# --- Technical Specification Models ---
@admin.register(CPUSpec)
class CPUSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'socket', 'tdp_watts')
    search_fields = ('component__name',)
    list_filter = ('socket',)

@admin.register(MotherboardSpec)
class MotherboardSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'socket', 'form_factor', 'memory_generation')
    search_fields = ('component__name',)
    list_filter = ('socket', 'form_factor', 'memory_generation')

@admin.register(RAMSpec)
class RAMSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'generation', 'speed_mhz')
    search_fields = ('component__name',)
    list_filter = ('generation',)

@admin.register(GPUSpec)
class GPUSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'vram_gb', 'length_mm', 'tdp_watts', 'recommended_psu_wattage')
    search_fields = ('component__name',)

@admin.register(PSUSpec)
class PSUSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'wattage', 'efficiency', 'is_modular')
    search_fields = ('component__name',)
    list_filter = ('efficiency', 'is_modular')

@admin.register(CaseSpec)
class CaseSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'max_form_factor', 'max_gpu_length_mm')
    search_fields = ('component__name',)
    list_filter = ('max_form_factor',)

@admin.register(CoolerSpec)
class CoolerSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'is_liquid_cooler', 'radiator_size_mm')
    search_fields = ('component__name',)
    list_filter = ('is_liquid_cooler',)

@admin.register(StorageSpec)
class StorageSpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'drive_type', 'capacity_gb')
    search_fields = ('component__name',)
    list_filter = ('drive_type',)
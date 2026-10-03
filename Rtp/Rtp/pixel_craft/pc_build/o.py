import os
import sys
import django

# 1. Boot up the Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pixel_craft.settings') 
django.setup()

# 2. Safely import models
from pc_build.models import Components

# Dataset
components_data = [
    {"name": "Radeon RX 6600", "brand": "AMD", "category": "GPU", "specs": {"vram": "8GB", "architecture": "RDNA 2"}, "image_url": "http://127.0.0.1:8000/media/component_images/AMD_RX_6600.png"},
    {"name": "Radeon RX 7900 XT", "brand": "AMD", "category": "GPU", "specs": {"vram": "20GB", "architecture": "RDNA 3"}, "image_url": "http://127.0.0.1:8000/media/component_images/AMD_RX_7900_XT.png"},
    {"name": "Ryzen 5 5600X", "brand": "AMD", "category": "CPU", "specs": {"cores": 6, "threads": 12, "socket": "AM4"}, "image_url": "http://127.0.0.1:8000/media/component_images/AMD_Ryzen_5_5600X.png"},
    {"name": "Ryzen 7 5800X", "brand": "AMD", "category": "CPU", "specs": {"cores": 8, "threads": 16, "socket": "AM4"}, "image_url": "http://127.0.0.1:8000/media/component_images/AMD_Ryzen_7_5800X.png"},
    {"name": "Vengeance LPX 16GB", "brand": "Corsair", "category": "RAM", "specs": {"capacity": "16GB", "type": "DDR4", "speed": "3200MHz"}, "image_url": "http://127.0.0.1:8000/media/component_images/Corsair_Vengeance_LPX_16GB.png"},
    {"name": "Trident Z 32GB", "brand": "G.SKILL", "category": "RAM", "specs": {"capacity": "32GB", "type": "DDR4", "speed": "3600MHz"}, "image_url": "http://127.0.0.1:8000/media/component_images/G.SKILL_Trident_Z_32GB.png"},
    {"name": "Core i5-12400F", "brand": "Intel", "category": "CPU", "specs": {"cores": 6, "threads": 12, "socket": "LGA1700"}, "image_url": "http://127.0.0.1:8000/media/component_images/Intel_Core_i5-12400F.png"},
    {"name": "Core i7-12700K", "brand": "Intel", "category": "CPU", "specs": {"cores": 12, "threads": 20, "socket": "LGA1700"}, "image_url": "http://127.0.0.1:8000/media/component_images/Intel_Core_i7-12700K.png"},
    {"name": "GeForce RTX 3060", "brand": "NVIDIA", "category": "GPU", "specs": {"vram": "12GB", "architecture": "Ampere"}, "image_url": "http://127.0.0.1:8000/media/component_images/NVIDIA_RTX_3060.png"},
    {"name": "GeForce RTX 4070", "brand": "NVIDIA", "category": "GPU", "specs": {"vram": "12GB", "architecture": "Ada Lovelace"}, "image_url": "http://127.0.0.1:8000/media/component_images/NVIDIA_RTX_4070.png"}
]

# CLEAN DB
Components.objects.all().delete()
print("🧹 Cleaned database...")

# INSERT DATA
for data in components_data:
    comp = Components.objects.create(
        name=data["name"],
        brand=data["brand"],
        category=data["category"],
        specs=data["specs"],  # <-- This is the fixed line
        image_url=data["image_url"]
    )

print("✅ Successfully seeded database!")
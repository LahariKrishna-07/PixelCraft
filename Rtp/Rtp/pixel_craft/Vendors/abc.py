from pc_build.models import Components

all_items = Components.objects.all()

for item in all_items:
    # 1. Print the base component info
    print(f"Product: {item.name} ({item.category})")
    
    # 2. Access the specific bridging tables based on the category
    if item.category == 'CPU' and hasattr(item, 'cpu_spec'):
        print(f" -> Socket: {item.cpu_spec.socket.name}")
        print(f" -> Power Draw: {item.cpu_spec.tdp_watts}W")
        
    elif item.category == 'GPU' and hasattr(item, 'gpu_spec'):
        print(f" -> Recommended PSU: {item.gpu_spec.recommended_psu_wattage}W")
        
    elif item.category == 'PSU' and hasattr(item, 'psu_spec'):
        print(f" -> Output: {item.psu_spec.wattage}W ({item.psu_spec.efficiency})")
        
    print("-" * 20)
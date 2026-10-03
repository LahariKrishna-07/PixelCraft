from django.db.models import Q
from pc_build.models import CustomBuild

class HardwareMatchmaker:
    """Evaluates an ongoing custom build and returns auto-filtering parameters 
    to guarantee 100% component compatibility in the catalog view."""
    
    def __init__(self, build_id):
        self.build = CustomBuild.objects.prefetch_related('items__inventory_item__component').get(id=build_id)
        self.parts = {item.inventory_item.component.category: item.inventory_item.component for item in self.build.items.all()}

    def get_compatibility_filters(self, targeting_category):
        """Generates dynamic Django ORM filters based on parts already in the build."""
        filters = Q(category=targeting_category)
        
        # Extract existing core selections if present
        cpu = self.parts.get('CPU')
        mobo = self.parts.get('Motherboard')
        gpu = self.parts.get('GPU')
        case = self.parts.get('Case')

        # --- RULESET 1: SYSTEM ARCHITECTURE (CPU & MOTHERBOARD BOUNDARIES) ---
        if targeting_category == 'Motherboard' and cpu and hasattr(cpu, 'cpu_spec'):
            # Board must match CPU Socket
            filters &= Q(motherboard_spec__socket=cpu.cpu_spec.socket)
            
        if targeting_category == 'CPU' and mobo and hasattr(mobo, 'motherboard_spec'):
            # CPU must match Board Socket
            filters &= Q(cpu_spec__socket=mobo.motherboard_spec.socket)

        # --- RULESET 2: MEMORY GENERATION (RAM MATCHES MOTHERBOARD) ---
        if targeting_category == 'RAM' and mobo and hasattr(mobo, 'motherboard_spec'):
            # RAM must be the exact gen supported by the board slots
            filters &= Q(ram_spec__generation=mobo.motherboard_spec.memory_generation)
            
        if targeting_category == 'Motherboard' and self.parts.get('RAM') and hasattr(self.parts['RAM'], 'ram_spec'):
            # If RAM is chosen first, board must match its generation
            filters &= Q(motherboard_spec__memory_generation=self.parts['RAM'].ram_spec.generation)

        # --- RULESET 3: THERMAL MOUNTING (COOLER CLAMPS TO SOCKET) ---
        if targeting_category == 'Cooling' and cpu and hasattr(cpu, 'cpu_spec'):
            # Cooler brackets must include support for this CPU socket
            filters &= Q(cooler_spec__supported_sockets=cpu.cpu_spec.socket)

        # --- RULESET 4: PHYSICAL DIMENSIONS (GPU CHASSIS CLEARANCE) ---
        if targeting_category == 'GPU' and case and hasattr(case, 'case_spec'):
            # Graphics card length cannot exceed case workspace clearance
            filters &= Q(gpu_spec__length_mm__lte=case.case_spec.max_gpu_length_mm)
            
        if targeting_category == 'Case' and gpu and hasattr(gpu, 'gpu_spec'):
            # Case layout must support the running length of the chosen GPU
            filters &= Q(case_spec__max_gpu_length_mm__gte=gpu.gpu_spec.length_mm)

        # --- RULESET 5: FORM FACTORS (MOTHERBOARD SIZES INSIDE CASE) ---
        if targeting_category == 'Motherboard' and case and hasattr(case, 'case_spec'):
            # Case form choices limit how wide the motherboard can be
            # e.g., if max is mATX, choices can be mATX or ITX, but not ATX or E-ATX
            allowed_factors = ['ITX']
            if case.case_spec.max_form_factor in ['mATX', 'ATX', 'E-ATX']: allowed_factors.append('mATX')
            if case.case_spec.max_form_factor in ['ATX', 'E-ATX']: allowed_factors.append('ATX')
            if case.case_spec.max_form_factor == 'E-ATX': allowed_factors.append('E-ATX')
            filters &= Q(motherboard_spec__form_factor__in=allowed_factors)

        return filters
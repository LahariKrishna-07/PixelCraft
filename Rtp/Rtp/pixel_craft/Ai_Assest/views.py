import os
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from pc_build.models import CustomBuild

# Safely extract the token string configuration
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

SYSTEM_INSTRUCTION = """
You are the Pixel Craft AI Hardware Architect, an elite custom computer engineering assistant. 
Your purpose is to guide users through diagnostic checks, optimization pathways, budget balancing, and part selection.
- Be precise, technical, yet highly approachable. Define deep concepts inline if needed.
- Format responses cleanly with Markdown (use bolding, bullets, and short tables for specification breakdowns).
- If context about the user's current ongoing custom configuration build is injected, use it to give contextual feedback.
- Reject questions unrelated to computers, technology, hardware, or electronics gracefully.
"""
@login_required
def chat_interface(request):
    """Renders the fullscreen dark sci-fi assistant interface node with predictive initial analysis."""
    build_id = request.GET.get('build_id')
    build_context = None
    ai_initial_analysis = None
    
    if build_id:
        build_context = get_object_or_404(CustomBuild, id=build_id, user=request.user)
        
        # 1. DYNAMIC WATTAGE CALCULATION VECTOR (Synchronized with main cockpit view dashboard logic)
        calculated_total_wattage = 0
        for item in build_context.items.all():
            comp = item.inventory_item.component
            slot = comp.category
            
            # Run our checklist across common database electrical power field columns
            item_wattage = 0
            for field_name in ['wattage', 'tdp', 'power', 'power_draw', 'power_consumption']:
                if hasattr(comp, field_name):
                    val = getattr(comp, field_name)
                    if val:
                        item_wattage = val
                        break
            
            # Hardcoded simulation fallback metrics to protect UI alignment
            if not item_wattage and slot != 'PSU':
                if slot == 'CPU': item_wattage = 125
                elif slot == 'GPU': item_wattage = 120
                elif slot == 'Motherboard': item_wattage = 50
                elif slot == 'RAM': item_wattage = 10
                elif slot == 'Storage': item_wattage = 10
                elif slot == 'Cooling': item_wattage = 25

            try:
                if item_wattage and slot != 'PSU':
                    if isinstance(item_wattage, str):
                        digits = ''.join(filter(str.isdigit, item_wattage))
                        item_wattage = int(digits) if digits else 0
                    calculated_total_wattage += int(item_wattage)
            except (ValueError, TypeError):
                pass

        # Explicitly assign calculated total wattage so the telemetry sidebar can pick it up
        build_context.total_estimated_wattage = calculated_total_wattage

        # 2. Compile immediate tracking profile parameters for greeting analysis
        installed_parts = [
            f"- {item.inventory_item.component.category}: {item.inventory_item.component.name} (₹{item.inventory_item.price})" 
            for item in build_context.items.all()
        ]
        
        if installed_parts:
            parts_manifest = "\n".join(installed_parts)
            
            # Safe Fallback PSU sufficiency calculation
            if hasattr(build_context, 'is_psu_sufficient'):
                is_safe = build_context.is_psu_sufficient
            else:
                is_safe = calculated_total_wattage < 600

            psu_status = "SUFFICIENT_POWER_HEADROOM" if is_safe else "CRITICAL_POWER_OVERHEAD_ALERT"
            
            diagnostic_prompt = f"""
            The user has initialized an active telemetry link to their build workspace.
            
            [SYSTEM_PROFILE]:
            Rig Name: {build_context.name}
            Current Valuation: ₹{build_context.total_build_price}
            Power Draw Estimate: {calculated_total_wattage} Watts
            PSU Safety Status Flag: {psu_status}
            
            [INSTALLED_HARDWARE_MODULES]:
            {parts_manifest}
            
            INSTRUCTION: Write a professional, highly concise, high-tech engineering introduction greeting the user.
            - Provide a rapid markdown bullet-point check-list summarizing their current build slots.
            - Explicitly call out any immediate warnings (e.g., if the PSU safety flag is failing, or if critical slots like CPU or RAM are completely missing).
            - Keep it tight, technical, and formatted matching a terminal diagnostic readout.
            """
            
            try:
                model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash',
                    system_instruction=SYSTEM_INSTRUCTION
                )
                response = model.generate_content(diagnostic_prompt)
                ai_initial_analysis = response.text
            except Exception as e:
                ai_initial_analysis = f"### [SYSTEM_DIAGNOSTICS_WARNING]\nTelemetry parsing connection timeout. Core hardware lines mapped locally but active AI evaluation link reported: {str(e)}"
        else:
            ai_initial_analysis = "System canvas is currently empty! Use the blueprint cockpit to mount component units so I can trace your internal architecture pipelines."

    return render(request, 'Ai_Assest/chat.html', {
        'build_context': build_context,
        'ai_initial_analysis': ai_initial_analysis
    })
@csrf_exempt
@login_required
def stream_chat_response(request):
    """Streams token chunks straight from the Gemini endpoint API to the template layer securely."""
    if request.method == 'POST':
        try:
            # Safely unpack the incoming raw request bytes
            raw_data = request.body.decode('utf-8', errors='ignore')
            data = json.loads(raw_data)
            
            user_message = data.get('message', '')
            history = data.get('history', [])
            build_id = data.get('build_id', None)
        except Exception as parse_err:
            return JsonResponse({'error': f'Malformed JSON input stream payload: {str(parse_err)}'}, status=400)
        
        # 1. Compile contextual system profile text if user is building a live rig
        extended_context = ""
        if build_id:
            try:
                build = CustomBuild.objects.get(id=build_id, user=request.user)
                installed_parts = [f"- {item.inventory_item.component.category}: {item.inventory_item.component.name} (₹{item.inventory_item.price})" for item in build.items.all()]
                extended_context = f"\n[CURRENT_USER_BUILD_CONTEXT]:\nRig Name: {build.name}\nTotal Price: ₹{build.total_build_price}\nEstimated Load: {getattr(build, 'total_estimated_wattage', 0)}W\nInstalled Modules:\n" + "\n".join(installed_parts)
            except CustomBuild.DoesNotExist:
                pass

        # 2. Re-map conversation history into the Google content structure protocol array safely
        contents = []
        for msg in history:
            msg_content = msg.get('content', '')
            # Sanitize input types and drop empty elements securely
            if msg_content and str(msg_content).strip():
                contents.append({
                    'role': 'user' if msg.get('role') == 'user' else 'model',
                    'parts': [str(msg_content).strip()]
                })
            
        # Append latest prompt entry token alongside embedded contextual metadata frames
        contents.append({
            'role': 'user',
            'parts': [f"{user_message}\n\n{extended_context}"]
        })

        # 3. Spin up the model layer instance array matrix safely
        try:
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=SYSTEM_INSTRUCTION
            )
        except Exception as model_err:
            return JsonResponse({'error': f'Failed to initialize GenAI Model engine: {str(model_err)}'}, status=500)

        # 4. Stream response generator closure loop
        def generate_stream():
            try:
                response = model.generate_content(contents, stream=True)
                for chunk in response:
                    if chunk and hasattr(chunk, 'text') and chunk.text:
                        data_payload = json.dumps({'text': chunk.text})
                        yield f"data: {data_payload}\n\n"
            except Exception as e:
                error_payload = json.dumps({'error': f'Gemini Runtime Engine Disruption: {str(e)}'})
                yield f"data: {error_payload}\n\n"

        response = StreamingHttpResponse(generate_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # Prevents Nginx from caching stream packets proxy-side
        return response

    return JsonResponse({'error': 'Invalid Request Node'}, status=400)
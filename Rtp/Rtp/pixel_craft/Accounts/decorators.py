from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

# 1. Bouncer for Ordinary Users (Keeps Vendors OUT)
def ordinary_user_required(view_func):
    def wrapper(request, *args, **kwargs):
        # If they aren't logged in, redirect to standard login
        if not request.user.is_authenticated:
            return redirect('Login') 
            
        try:
            # If Django finds a vendor profile, they are a Vendor. Kick them to the vendor dashboard.
            vendor = request.user.vendor
            return redirect('Vendors_Home') 
        except ObjectDoesNotExist:
            # If it throws an error, they DO NOT have a vendor profile. Let them in!
            return view_func(request, *args, **kwargs)
            
    return wrapper

# 2. Bouncer for Vendors (Keeps Ordinary Users OUT)
def vendor_required(view_func):
    def wrapper(request, *args, **kwargs):
        # If they aren't logged in, redirect to vendor login
        if not request.user.is_authenticated:
            return redirect('vendor_login')
            
        try:
            # If they have a vendor profile, let them in!
            vendor = request.user.vendor
            return view_func(request, *args, **kwargs)
        except ObjectDoesNotExist:
            # If they don't have a vendor profile, kick them to the normal homepage.
            return redirect('home') 
            
    return wrapper
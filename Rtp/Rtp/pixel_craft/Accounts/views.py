
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from .forms import LoginForm,RegisterForm
from .forms import UserUpdateForm
from django.shortcuts import render
from .decorators import ordinary_user_required


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from Vendors.models import Vendor


def Login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST) 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if Vendor.objects.filter(user=user).exists():
                    return redirect('/Vendors/')  
                else:
                    return redirect('/')           

            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'Accounts/Login.html', {'form': form})


def Logout(request):
    logout(request)
    return redirect(Login)

from Vendors.models import Vendor
def Register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            if form.cleaned_data['is_vendor']:
                Vendor.objects.create(
                    user=user,
                    shop_name=user.username  
                )

            return redirect('Login')
    else:
        form = RegisterForm()
    return render(request, 'Accounts/Register.html', {'form': form})

@login_required 
@ordinary_user_required  
def Profile(request):
    user=request.user
    return render(request,'Accounts/Profile.html',{'user':user})


@login_required
@ordinary_user_required
def Profile_edit(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'Accounts/profile_edit.html', {'form': form})
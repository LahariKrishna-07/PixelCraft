from django.shortcuts import render
from Accounts.decorators import *
# Create your views here.

def Home(request):
    return render(request,'Home/Home.html')
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout

# Create your views here.
@login_required
def homepage(request):
    return render(request, 'dashboard.html')


def general(request):
    return render(request, 'forms/general.html') 

@login_required
def documents(request):
    return render(request, 'documents.html')


def logout_view(request):
    logout(request)
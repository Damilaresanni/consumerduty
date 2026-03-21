from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product, ProductType

# Create your views h

def products(request):
   return render(request, 'products.html')
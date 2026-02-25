from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UploadDocumentForm
from .models import Document, Product

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


@login_required
def document_list(request):
    documents = Document.objects.filter(uploaded_by=request.user).select_related("product")
    return render(request, "documents/document_list.html", {"documents":document_list})


@login_required
def upload_document(request):
    if request.method == "POST":
        form = UploadDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document=form.save(commit=False)
            document.uploaded_by= request.user
            document.mime_type = getattr(document.file,"content_type", "")
            document.size_bytes = document.file.size
            document.save()
            
            return redirect("documents:list")
    else:
        form = UploadDocumentForm()
        
    return render(request, "documents/upload.html", {"form":form})
        


@login_required
def product_documents(request, product_id):
    product = get_object_or_404(Product,id=product_id)
    documents = product.documents.filter(uploaded_by=request.user)
    return render(request, "documents/product_documents.html", {"product":product,"documents":documents})



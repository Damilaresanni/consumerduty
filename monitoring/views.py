from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UploadDocumentForm
from .models import Document, Product, RuleBasedFinding
from  monitoring.models import Document
import mimetypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import RuleBasedFindingSerializer
from .tasks import process_document
from product.models import Product, ProductType




# Create your views here.


@login_required
def homepage(request):
    products = Product.objects.all()
    return render(request, 'dashboard.html', {'products':products})


def general(request):
    return render(request, 'forms/general.html') 

@login_required
def documents(request):
    docs = Document.objects.all().order_by('-created_at')
    products = Product.objects.select_related()
    product_type = ProductType.choices
    return render(request, 'documents.html',{'documents':docs, 'products':products,  'product_types':product_type} )


def logout_view(request):
    logout(request)


@login_required
def document_list(request):
    documents = Document.objects.filter(uploaded_by=request.user).select_related("product")
    return render(request, "documents/document_list.html", {"documents":document_list})


# @login_required
# def upload_document(request):
#     if request.method == "POST":
#         file_obj = request.FILES['file']
#         form = UploadDocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             document=form.save(commit=False)
#             document.uploaded_by= request.user
#             document.mime_type = file_obj.content_type
#             # document.mime_type = getattr(document.file,"content_type", "")
#             document.size_bytes = document.file.size
#             document.save()
            
#             process_document.delay(document.id) # type: ignore
#             return redirect("documents")
#     else:
#         form = UploadDocumentForm()
        
#     return render(request, "documents/upload.html", {"form":form})
        


@login_required
def product_documents(request, product_id):
    product = get_object_or_404(Product,id=product_id)
    documents = product.documents.filter(uploaded_by=request.user) # type: ignore
    return render(request, "documents/product_documents.html", {"product":product,"documents":documents})




class RuledBasedFindingAPI(APIView):
    def get(self, request):
        findings = RuleBasedFinding.objects.all()
        serializer = RuleBasedFindingSerializer(documents, many=True)
    
        return Response(serializer.data)
    
@api_view(['GET'])   
def rule_based_finding_api(request):
    findings = RuleBasedFinding.objects.all()
    serializer = RuleBasedFindingSerializer(findings, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def document_status(request, doc_id):
    doc= Document.objects.get(id=doc_id)
    return Response({'status':doc.status})
    
    




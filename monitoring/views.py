from django.shortcuts import render, redirect
from .forms import UploadDocumentForm

# Create your views here.
def homepage(request):
    return render(request, 'index.html')


def upload_document(request):
    if request.method == "POST":
        form = UploadDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return redirect("success_page")
        
        else:
            form = UploadDocumentForm()
            
        return render(request, "upload.html", {"form":form})    
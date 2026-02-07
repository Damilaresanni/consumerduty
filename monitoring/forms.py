from django import forms
from . models import Document

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file", "title", "product"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class':'form-control'})
        }
        
        
    def clean_file(self):
        file = self.cleaned_data['file']
        
        max_size = 20 * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError("File to large (max 20MB).")
        
        allowed_extensions = [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        file_ext = getattr(file, "content_type", None)
        if file_ext not in allowed_extensions:
            raise forms.ValidationError("Unsupported file type.")
        
        return file
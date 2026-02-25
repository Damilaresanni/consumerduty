from rest_framework import serializers
from . models import Document

class DocumentSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    
    
    class Meta:
        model = Document
        fields = [
         "id",
         "title",
         "file", 
         "mime_type",
         "size_bytes", 
         "status", 
         "created_at", 
         "processed_at", 
         "product",
         "product_name",
        ]
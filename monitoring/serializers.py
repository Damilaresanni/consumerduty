from rest_framework import serializers
from . models import Document, RuleBasedFinding


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
        
        

class RuleBasedFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleBasedFinding
        fields = ['id', 'rule_name', 'fca_rule_ref', 'description', 
                  'severity','start_char','end_char','snippet', 'created_at']
        


        
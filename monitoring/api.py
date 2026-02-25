from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer


@api_view(["GET"])
def document_list_api(request):
    docs = Document.objects.all()
    return Response(DocumentSerializer(docs, many=True).data)


@api_view(["GET"])
def product_documents_api(request, product_id):
    docs = Document.objects.filter(product_id=product_id)
    return Response(DocumentSerializer(docs, many=True).data)
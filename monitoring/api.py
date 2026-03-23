from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Document, RuleBasedFinding
from.rag import search_similar_chunks, build_prompt, call_llm
from .serializers import DocumentSerializer
from .forms import UploadDocumentForm
from rest_framework import status
from .models import Product
from celery.result import AsyncResult
from .tasks import process_document


@api_view(["DELETE"])
def delete_document(request, pk):
    Document.objects.filter(id=pk).delete()
    return Response({"status": "deleted"})

@api_view(["GET"])
def get_document(request, pk):
    doc = Document.objects.select_related("product").get(id=pk)
    return Response({
        "id": doc.id,
        "name": doc.title,
        "product": {
            "id": doc.product.id, # type: ignore
            "product_name": doc.product.product_name, # type: ignore
            "description": doc.product.description, # type: ignore
            "product_type": doc.product.product_type, # type: ignore
        }
    })

@api_view(["POST"])
def update_product(request, pk):
    product = Product.objects.get(id=pk)
    product.product_name = request.data.get("product_name")
    product.description = request.data.get("description")
    product.product_type = request.data.get("product_type")
    product.save()
    return Response({"status": "updated"})


@api_view(["GET"])
def document_list_api(request):
    docs = Document.objects.all()
    return Response(DocumentSerializer(docs, many=True).data)


@api_view(["GET"])
def product_documents_api(request, product_id):
    docs = Document.objects.filter(product_id=product_id)
    return Response(DocumentSerializer(docs, many=True).data)



@api_view(["POST"])
def create_product(request):
    product_name = request.data.get("product_name")
    description = request.data.get("description")
    product_type = request.data.get("product_type")

    if not product_name or not product_type:
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    product = Product.objects.create(
        product_name=product_name,
        description=description,
        product_type=product_type,
    )

    return Response({
        "id": product.id,
        "product_name": product.product_name,
        "description": product.description,
        "product_type": product.product_type,
    }, status=status.HTTP_201_CREATED)




@api_view(["POST"])
def upload_document(request):
    #Note: The UplaodDocumentForm fucntion is to validate the incoming 
    #http request.
    
    
    #instantiates a form instance by calling the UplaodDocumentForm 
    # which accepts two parameters the POST request abd the file on 
    # the file in the POST request.
    form = UploadDocumentForm(request.POST, request.FILES)

    #confirms the validity of the form if true else return 
    # an error response.
    if not form.is_valid():
        return Response({"errors": form.errors}, status=400)

    #Gets the product_id from the incoming POST requests 
    # and stores it in variable product_id.
    product_id = request.POST.get("product_id")

    # A try and exception block to check the existence of the requested product.
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Invalid Product ID"}, status=400)

    #creates a form instance and saves it as documment.
    document = form.instance
    
    #adds the respectives fields to the document instance 
    # before being stored. 
    document.product = product
    document.uploaded_by = request.user
    document.mime_type = request.FILES["file"].content_type
    document.size_bytes = request.FILES["file"].size

    #saves and persists the document instance onto the database
    document = form.save() 
    
    #process_document function is used to initiate a celery task
    #for initiating document processing tasks.
    task = process_document.delay(document.id) # type: ignore

    #return a json instance of the created or saved document
    return Response(
        {
            "id": document.id,
            "title": document.title,
            "product_id": document.product_id,
            "product_name": document.product.product_name,
            "task_id":task.id,
            "status":"processing",
        },
        status=201,
    )




@api_view(["POST"])
def rag_query(request,product_id):
    product_id = request.data.get("product_id")
    query = request.data.get("query")
    if not query:
        return Response({"error": "Query is required"}, status=400)
    
    results = search_similar_chunks(query, product_id=product_id, top_k=5)
    return Response({"results": results})


@api_view(["POST"])
def rag_with_findings(request):
    product_id = request.data.get("product_id")
    query = request.data.get("query")
    if not query:
        return Response({"error": "Query is required"}, status=400)
    
    if not product_id:
        return Response({"error": "product_id is required"}, status=400)
    
    chunks = search_similar_chunks(query, product_id=product_id, top_k=10)
    
    doc_ids = {c["document_id"] for c in chunks} 
    
    if not chunks:
        return Response({"answer": "No relevant data found", "chunks": [], "findings": []})
    
    findings = RuleBasedFinding.objects.filter(document_id__in =doc_ids)
    
    prompt =  build_prompt(query, chunks, findings)
    
    answer = call_llm(prompt)
    
    return Response({
        "answer":answer,
        "chunks":chunks,
        "findings": [
            {
                "document_id":f.document.id,
                "rule_name": f.rule_name,
                "fca_rule_ref":f.fca_rule_ref,
                "severity": f.severity,
                "snippet": f.snippet,
            }
            for f in findings
        ],
    })
    
    



@api_view(['GET'])
def check_task_status(request, task_id):
    res = AsyncResult(task_id)
    # response.state will be PENDING, STARTED, SUCCESS, or FAILURE
    return Response({
        "task_id": task_id,
        "status": res.state,
        "result": res.result if res.ready() else None
    })
    
    
    
    
    
    
    


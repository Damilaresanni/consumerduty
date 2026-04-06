from django.urls import path
from . import views
from . import api
from . views import RuledBasedFindingAPI, rule_based_finding_api


urlpatterns = [
    path('forms/', views.general, name='general'),
    path('documents/', views.documents, name= 'documents'),
    path("", views.document_list, name="doc_list"), 
    # path("upload/", views.upload_document, name="doc_uplaod"),
    path("product/<int:product_id>/", views.product_documents,name="doc_by_product" ),
    
    
    
    #API
    path("api/documents/", api.document_list_api, name="api_doc_list"),
    path("api/products/<int:product_id>/documents/", api.product_documents_api, name="api_doc_by_product"),
    path("api/findings/" , rule_based_finding_api, name= "findings"),
    
    path("api/products/<int:product_id>/rag/", api.rag_query, name="rag_query"),
    path("api/products/<int:product_id>/rag/", api.rag_with_findings),

    path("api/products/create/", api.create_product), 
    path("api/documents/upload/", api.upload_document),
    path("api/tasks/status/<str:task_id>/" , api.check_task_status),
    path("api/rag/query/" , api.rag_with_findings),
    path("api/documents/<int:pk>/delete/", api.delete_document),
    path("api/documents/<int:pk>/edit/", api.update_product),
    path("api/test/nlp", api.test_nlp)

] 





    

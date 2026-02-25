from django.urls import path
from . import views, api


app_name = "monitoring"

urlpatterns = [
    path('forms/', views.general, name='general'),
    path('documents/', views.documents, name= 'documents'),
    path("", views.document_list, name="doc_list"), 
    path("upload/", views.upload_document, name="doc_uplaod"),
    path("product/<int:product_id>/", views.product_documents,name="doc_by_product" ),
    
    
    
    #API
    path("api/documents/", api.document_list_api, name="api_doc_list"),
    path("api/products/<int:product_id>/documents/", api.product_documents_api, name="api_doc_by_product")
] 





    

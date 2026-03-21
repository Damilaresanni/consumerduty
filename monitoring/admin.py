from django.contrib import admin

from .models import Document, DocumentChunk, ConsumerDutyReview, Product
# Register your models here.

admin.site.register(Document)
admin.site.register(DocumentChunk)
admin.site.register(ConsumerDutyReview)
admin.site.register(Product)

admin.site.site_header = "Consumer Duty Admin"
admin.site.site_title = "Consumer Duty Portal"
admin.site.index_title = "Welcome to the Document Management System"
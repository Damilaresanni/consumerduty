from django.db import models
from product.models import Product
from django.conf import settings



class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
        


    

    
    
class ConsumerDutyReview(BaseModel):
    class VulnerableOptions(models.TextChoices):
        yes = "yes", "Yes"
        no = "no", "No"
        mixed = "mixed", "Mixed"
        
        
     
    class StatusLevel(models.TextChoices):
        low = "low", "Low"
        mid = "mid", "Mid"
        high = "high", "High"
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="consumer_duty_reviews"
    )

    review_frequency = models.PositiveIntegerField()
    last_consumer_duty_review_date = models.DateTimeField()
    notes_on_known_risks = models.TextField(null=True, blank=True)
    
    
    risk_tolerance_assumption = models.CharField(
        max_length=255,
        choices=StatusLevel.choices,
        null = True,
        blank = True
    )
    vulnerability_consideration = models.CharField(
        max_length=255,
        choices=VulnerableOptions.choices,
        null = True,
        blank = True
    )

    def __str__(self):
        return f"{self.product.product_name} Review"



class Document(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending" , "Pending"
        PROCCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        
        
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="documents", null=True, blank=True)
    title = models.CharField(max_length=255)    
    file = models.FileField(upload_to="uploads/%y/%m/%d/")
    mime_type= models.CharField(max_length=100, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="Uploaded_documents"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file.name} uploaded by {self.uploaded_by}"
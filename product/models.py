from django.db import models


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
        
        
class Status(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ARCHIVED = "archived", "Archived"

class ProductType(models.TextChoices):
    LOAN = "loan" , "Loan"
    INSURANCE = "insurance", "Insurance"
    SAVINGS =  "savings", "Savings"

class Product(BaseModel):
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    launch_date = models.DateTimeField(null=True,blank=True)
    product_version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey(
        "self",
        null = True,
        blank=True,
        on_delete=models.SET_NULL
    )
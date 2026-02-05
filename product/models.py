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
    

class CustomerType(models.TextChoices):
    retail = "retail" , "Retail"
    professional = "profesional", "Profesional"
    mixed =  "mixed", "Mixed"



class StatusLevel(models.TextChoices):
    low = "low", "Low"
    mid = "mid", "Mid"
    high = "high", "High"
    
    

class VulnerableOptions(models.TextChoices):
    yes = "yes", "Yes"
    no = "no", "No"
    mixed = "mixed", "Mixed"

class Product(BaseModel):
    product_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
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
    
    intended_consumer_type = models.CharField(
        max_length=225,
        choices=CustomerType.choices,
        null = True,
        blank = True
    )
    
    financial_sophistication_level= models.CharField(
        max_length=255,
        choices= StatusLevel.choices ,
        null = True,
        blank = True  
    )
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
    
    product_owner = models.CharField(max_length=255, null=True,blank=True)
    
    
    def __str__(self): 
        return self.product_name
    
  
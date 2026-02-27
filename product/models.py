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


    
class Product(BaseModel):
    product_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
    )
   
   
    
    # intended_consumer_type = models.CharField(
    #     max_length=225,
    #     choices=CustomerType.choices,
    #     null = True,
    #     blank = True
    # )
    
    # financial_sophistication_level= models.CharField(
    #     max_length=255,
    #     choices= StatusLevel.choices ,
    #     null = True,
    #     blank = True  
    # )
    
    
   
    
    
    def __str__(self): 
        return self.product_name
    
  
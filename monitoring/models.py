from django.db import models
from product.models import Product



class VulnerableOptions(models.TextChoices):
    yes = "yes", "Yes"
    no = "no", "No"
    mixed = "mixed", "Mixed"
    
    
class StatusLevel(models.TextChoices):
    low = "low", "Low"
    mid = "mid", "Mid"
    high = "high", "High"
    
    
class ConsumerDutyReview(models.Model):
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

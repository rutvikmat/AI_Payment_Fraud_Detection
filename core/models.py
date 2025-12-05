from django.db import models

class FraudAlert(models.Model):
    FRAUD_TYPES = (
        ('SCREENSHOT_TAMPERED', 'Fake/Edited Screenshot'),
        ('AMOUNT_MISMATCH', 'Fuel vs Bill Mismatch'),
        ('DUPLICATE', 'Duplicate Transaction'),
        ('ANOMALY', 'Suspicious Pattern'),
        ('PUMP_MISMATCH', 'CCTV vs Bill Mismatch'),
    )

    # Basic Details
    customer_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=50, unique=True)
    
    # Transaction Data
    fuel_dispensed = models.FloatField(help_text="Liters dispensed (from Pump/CCTV)")
    bill_amount = models.FloatField(help_text="Amount claimed by customer")
    
    # Evidence Files
    payment_screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
    pump_image = models.ImageField(upload_to='pump_cctv/', blank=True, null=True, help_text="Upload photo of Pump Meter (CCTV Sim)")
    ela_evidence = models.ImageField(upload_to='ela_evidence/', blank=True, null=True, help_text="Forensic Analysis Image")
    
    # Fraud Status
    is_fraud = models.BooleanField(default=False)
    fraud_reason = models.CharField(max_length=255, blank=True, null=True)
    fraud_type = models.CharField(max_length=50, choices=FRAUD_TYPES, blank=True, null=True)
    
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {'FRAUD' if self.is_fraud else 'Clean'}"
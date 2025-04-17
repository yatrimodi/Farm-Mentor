from time import timezone

from django.db import models
from django.contrib.auth.models import User

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to User model
    message = models.TextField()  # Message sent by the user
    response = models.TextField()  # Response from the chatbot
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the chat was created

    def __str__(self):
        return f"Chat with {self.user.username} at {self.created_at}"

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Fertilizers', 'Fertilizers'),
        ('Pesticides', 'Pesticides'),
        ('Equipment', 'Equipment'),
        ('Labor', 'Labor'),
        ('Other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.amount}"

from django.db import models



class SoilMap(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="soil_maps/")
    soil_type = models.CharField(max_length=255, default="Unknown")
    suggested_crops = models.TextField(default="No suggestions")

    def __str__(self):
        return self.name

class SoilAnalysis(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="soil_images/")
    soil_type = models.CharField(max_length=255, null=True, blank=True)
    suggested_crops = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_fake = models.BooleanField(default=False)  # ✅ Ensure this field exists
    analyzed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name










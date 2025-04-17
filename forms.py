from django import forms
from django.contrib.auth.models import User
from .models import Expense , FarmerProfile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = ['farm_name', 'location', 'phone_number']

# Registration form
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password

# Login form (optional, but can be used for custom login)
class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

class FarmConditionForm(forms.Form):
    location = forms.CharField(max_length=100, label="Enter Location (City)")

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description']
from django import forms
from .models import SoilMap



from django import forms
from .models import SoilMap

class SoilMapForm(forms.ModelForm):
    class Meta:
        model = SoilMap
        fields = ['name', 'image']  # ✅ Use "image" instead of "soil_image"






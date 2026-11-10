from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import SiteReview


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class SiteReviewForm(forms.ModelForm):
    class Meta:
        model = SiteReview
        fields = ("experience", "expectations")
        labels = {
            "experience": "How has your experience with CodeBlog been?",
            "expectations": "What were you expecting from the site?",
        }
        widgets = {
            "experience": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Share what has worked well or what could be better."}),
            "expectations": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Tell us what you hoped to find or do on CodeBlog."}),
        }

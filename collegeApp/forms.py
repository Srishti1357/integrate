from django import forms
from .models import Student

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['approval']

from django import forms
from collegeApp.models import Student

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'event', 'type_of_visitor', 'phone', 'college','roll_no', 'college_id_card']

class IdUploadForm(forms.Form):
    image = forms.ImageField()
# Compare this snippet from User/Info/ocr_api.py:
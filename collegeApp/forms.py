# # from django import forms
# # from .models import Student

# # class ApprovalForm(forms.ModelForm):
# #     class Meta:
# #         model = Student
# #         fields = ['approval']


# from django import forms
# from .models import Student, College

# class StudentForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = '__all__'
#         exclude = ['id']

#     college = forms.ModelChoiceField(
#         queryset=College.objects.filter(active=True),  # Only active colleges
#         empty_label="Select an Active College"
#     )


from django import forms
from .models import Student, College

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['college'].queryset = College.objects.filter(active=True)
        self.fields['college'].empty_label = "Select an Active College"

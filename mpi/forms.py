from django import forms

from .models import Document

class MpiParameters(forms.Form):
    amount_of_process = forms.CharField(
        label='Amount of process',
        max_length=5,
        required=True,
    )

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file']
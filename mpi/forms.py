from django import forms

from .models import Document

class MpiParameters(forms.Form):
    amount_of_process = forms.CharField(
        label='Amount of process',
        max_length=5,
        required=True,
    )
    document_id = forms.ChoiceField(
    	choices = [],
    	label="Choose file", 
    	initial='', 
    	widget=forms.Select(), 
    	required=True
    	)

    def __init__(self, user, *args, **kwargs):
    	super(MpiParameters, self).__init__(*args, **kwargs)
    	if user.is_superuser:
    		self.fields['document_id'] = forms.ChoiceField(
    			choices = [(o.id, str(o)) for o in Document.objects.all()]
    			)
    	else:
	    	self.fields['document_id'] = forms.ChoiceField(
	    		choices = [(o.id, str(o)) for o in Document.objects.filter(user = user)]
	    		)

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file']
"""
Forms for contracts app.
"""
from django import forms
from .models import Milestone, Deliverable


class MilestoneForm(forms.ModelForm):
    """Form for creating and editing milestones."""
    
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'amount', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Milestone title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what will be delivered in this milestone'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class DeliverableForm(forms.ModelForm):
    """Form for uploading deliverables."""
    
    class Meta:
        model = Deliverable
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Deliverable title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of this deliverable'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class RevisionRequestForm(forms.Form):
    """Form for requesting revisions on a milestone."""
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Explain what needs to be revised...'
        }),
        label='Revision Notes'
    )

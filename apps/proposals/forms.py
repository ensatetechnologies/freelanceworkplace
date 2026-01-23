"""
Forms for proposals app.
"""
from django import forms
from .models import Proposal, ProposalAttachment


class ProposalForm(forms.ModelForm):
    """Form for creating and editing proposals."""
    
    class Meta:
        model = Proposal
        fields = ['cover_letter', 'bid_amount', 'estimated_duration']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Introduce yourself and explain why you are the best fit for this project...'
            }),
            'bid_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2 weeks, 1 month'
            }),
        }
        labels = {
            'cover_letter': 'Cover Letter',
            'bid_amount': 'Your Bid ($)',
            'estimated_duration': 'Estimated Delivery Time'
        }
    
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        
        if project:
            budget_display = f'${project.budget_min} - ${project.budget_max}'
            if project.budget_type == 'hourly':
                budget_display += '/hr'
            self.fields['bid_amount'].help_text = f'Project budget: {budget_display}'


class ProposalAttachmentForm(forms.ModelForm):
    """Form for proposal attachments."""
    
    class Meta:
        model = ProposalAttachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the file'
            }),
        }

"""
Forms for reviews app.
"""
from django import forms
from .models import Review


class ClientReviewForm(forms.ModelForm):
    """Form for clients reviewing freelancers."""
    
    class Meta:
        model = Review
        fields = [
            'overall_rating', 'quality_rating', 'communication_rating',
            'timeliness_rating', 'professionalism_rating', 'comment'
        ]
        widgets = {
            'overall_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'quality_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'communication_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'timeliness_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'professionalism_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience working with this freelancer...'
            }),
        }


class FreelancerReviewForm(forms.ModelForm):
    """Form for freelancers reviewing clients."""
    
    class Meta:
        model = Review
        fields = [
            'overall_rating', 'clarity_rating', 'communication_rating',
            'payment_rating', 'professionalism_rating', 'comment'
        ]
        widgets = {
            'overall_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'clarity_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'communication_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'payment_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'professionalism_rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience working with this client...'
            }),
        }

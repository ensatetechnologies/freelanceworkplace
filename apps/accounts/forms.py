"""
Forms for accounts app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from .models import User, FreelancerProfile, ClientProfile


class CustomSignupForm(SignupForm):
    """Custom signup form with role selection."""
    
    ROLE_CHOICES = [
        ('freelancer', 'I want to work as a Freelancer'),
        ('client', 'I want to hire Freelancers'),
    ]
    
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    
    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Form for updating user basic information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FreelancerProfileForm(forms.ModelForm):
    """Form for freelancer profile."""
    
    skills_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Python, Django, JavaScript, React...'
        }),
        help_text='Enter skills separated by commas'
    )
    
    class Meta:
        model = FreelancerProfile
        fields = [
            'title', 'bio', 'hourly_rate', 'experience_years',
            'availability', 'portfolio_url', 'github_url', 'linkedin_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full Stack Developer'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.skills:
            self.fields['skills_input'].initial = ', '.join(self.instance.skills)
    
    def clean_skills_input(self):
        skills_input = self.cleaned_data.get('skills_input', '')
        if skills_input:
            skills = [s.strip() for s in skills_input.split(',') if s.strip()]
            return skills
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.skills = self.cleaned_data.get('skills_input', [])
        if commit:
            instance.save()
        return instance


class ClientProfileForm(forms.ModelForm):
    """Form for client profile."""
    
    class Meta:
        model = ClientProfile
        fields = ['company_name', 'company_website', 'industry', 'company_size']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
        }

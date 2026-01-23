"""
Forms for projects app.
"""
from django import forms
from .models import Project, ProjectAttachment, Category


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""
    
    skills_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Python, Django, React, etc.'
        }),
        help_text='Enter skills separated by commas'
    )
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category', 'budget_type',
            'budget_min', 'budget_max', 'experience_level',
            'estimated_duration', 'deadline', 'is_urgent'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Describe your project in detail...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'budget_type': forms.Select(attrs={'class': 'form-select'}),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'estimated_duration': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        
        if self.instance and self.instance.skills_required:
            self.fields['skills_input'].initial = ', '.join(self.instance.skills_required)
    
    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        
        if budget_min and budget_max:
            if budget_max < budget_min:
                raise forms.ValidationError(
                    'Maximum budget must be greater than or equal to minimum budget.'
                )
        
        return cleaned_data
    
    def clean_skills_input(self):
        skills_input = self.cleaned_data.get('skills_input', '')
        if skills_input:
            skills = [s.strip() for s in skills_input.split(',') if s.strip()]
            return skills
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.skills_required = self.cleaned_data.get('skills_input', [])
        if commit:
            instance.save()
        return instance


class ProjectAttachmentForm(forms.ModelForm):
    """Form for project attachments."""
    
    class Meta:
        model = ProjectAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }


class ProjectSearchForm(forms.Form):
    """Form for project search and filtering."""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    budget_type = forms.ChoiceField(
        choices=[('', 'All Budget Types')] + list(Project.BudgetType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    experience_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + list(Project.ExperienceLevel.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_budget = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min budget'
        })
    )
    max_budget = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max budget'
        })
    )

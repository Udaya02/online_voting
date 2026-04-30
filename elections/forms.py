"""
Forms for creating and editing elections and candidates.
"""
from django import forms
from .models import Election, Candidate


class ElectionForm(forms.ModelForm):
    """Form for creating and editing elections."""

    class Meta:
        model = Election
        fields = ('title', 'description', 'start_date', 'end_date', 'status', 'is_public')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Election title',
                'id': 'id_election_title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Describe this election...',
                'rows': 4,
                'id': 'id_election_description',
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
                'id': 'id_election_start',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
                'id': 'id_election_end',
            }),
            'status': forms.Select(attrs={
                'class': 'form-input form-select',
                'id': 'id_election_status',
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
                'id': 'id_election_public',
            }),
        }

    def clean(self):
        """Validate that end_date is after start_date."""
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end <= start:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned


class CandidateForm(forms.ModelForm):
    """Form for adding and editing candidates."""

    class Meta:
        model = Candidate
        fields = ('name', 'party', 'bio', 'photo', 'position_order')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Candidate name',
                'id': 'id_candidate_name',
            }),
            'party': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Party or affiliation',
                'id': 'id_candidate_party',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Brief bio of the candidate...',
                'rows': 3,
                'id': 'id_candidate_bio',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-input form-file',
                'id': 'id_candidate_photo',
                'accept': 'image/*',
            }),
            'position_order': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Display order',
                'min': 0,
                'id': 'id_candidate_order',
            }),
        }

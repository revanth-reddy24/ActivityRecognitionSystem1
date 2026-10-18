from django import forms
from .models import Activity, Environment, ActivitySession

class ActivityFilterForm(forms.Form):
    ACTIVITY_CHOICES = [('', 'All Activities')] + list(Activity.ACTIVITY_TYPES)
    
    activity_type = forms.ChoiceField(
        choices=ACTIVITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    environment = forms.ModelChoiceField(
        queryset=Environment.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class EnvironmentForm(forms.ModelForm):
    class Meta:
        model = Environment
        fields = ['name', 'address', 'description', 'zones', 'wifi_channels', 'sensor_parameters']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'zones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter zones as JSON array'}),
            'wifi_channels': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter WiFi channels as JSON array'}),
            'sensor_parameters': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter sensor parameters as JSON object'}),
        }
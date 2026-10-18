from django import forms
from users.models import CustomUser
from .models import SystemConfig, ActivityModel
from notifications.models import NotificationRule
from activities.models import Environment

class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = ['key', 'value', 'category', 'description']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ActivityModelForm(forms.ModelForm):
    class Meta:
        model = ActivityModel
        fields = ['name', 'version', 'status', 'model_file', 'training_data']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'training_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class NotificationRuleForm(forms.ModelForm):
    class Meta:
        model = NotificationRule
        fields = ['name', 'activity_type', 'condition', 'priority', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'activity_type': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter condition as JSON'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }

class EnvironmentForm(forms.ModelForm):
    class Meta:
        model = Environment
        fields = ['name', 'address', 'description', 'is_active', 'zones', 'wifi_channels', 'sensor_parameters']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'zones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter as JSON'}),
            'wifi_channels': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter as JSON'}),
            'sensor_parameters': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter as JSON'}),
        }
class EnvironmentForm(forms.ModelForm):
    class Meta:
        model = Environment
        fields = ['name', 'address', 'description', 'is_active', 'zones', 'wifi_channels', 'sensor_parameters']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'zones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter as JSON'}),
            'wifi_channels': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter as JSON'}),
            'sensor_parameters': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter as JSON'}),
        }

class UserManagementForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }
from django.db import models
from django.utils import timezone
from users.models import CustomUser

class SystemConfig(models.Model):
    CONFIG_CATEGORIES = (
        ('general', 'General'),
        ('security', 'Security'),
        ('notification', 'Notification'),
        ('sensor', 'Sensor'),
        ('model', 'Model'),
    )
    
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    category = models.CharField(max_length=20, choices=CONFIG_CATEGORIES, default='general')
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
    
    def __str__(self):
        return self.key

class ActivityModel(models.Model):
    MODEL_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('training', 'Training'),
        ('error', 'Error'),
    )
    
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=MODEL_STATUS, default='inactive')
    performance_metrics = models.JSONField(default=dict, blank=True)
    model_file = models.FileField(upload_to='models/', blank=True, null=True)
    training_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_trained = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} v{self.version}"

class AuditLog(models.Model):
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('access', 'Access'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.model_name}"

class SystemPerformance(models.Model):
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    network_usage = models.FloatField()
    active_users = models.IntegerField()
    activities_processed = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Performance at {self.timestamp}"
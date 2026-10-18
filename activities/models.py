from django.db import models
from django.utils import timezone  # Add this import
from users.models import CustomUser

class Environment(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    zones = models.JSONField(default=list, blank=True)
    wifi_channels = models.JSONField(default=list, blank=True)
    sensor_parameters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('walking', 'Walking'),
        ('running', 'Running'),
        ('sitting', 'Sitting'),
        ('standing', 'Standing'),
        ('falling', 'Falling'),
        ('unusual', 'Unusual Activity'),
        ('cooking', 'Cooking'),
        ('sleeping', 'Sleeping'),
        ('exercising', 'Exercising'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    confidence_score = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)  # Now this will work
    duration = models.DurationField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    environment = models.ForeignKey(Environment, on_delete=models.SET_NULL, null=True, blank=True)
    sensor_data = models.JSONField(default=dict, blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

class ActivitySession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    activities = models.ManyToManyField(Activity)
    total_duration = models.DurationField(null=True, blank=True)
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username}"

class MultiPersonActivity(models.Model):
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Multi-person activity at {self.timestamp}"

class PersonActivity(models.Model):
    multi_activity = models.ForeignKey(MultiPersonActivity, on_delete=models.CASCADE)
    # Allow null user to support anonymous/unknown detected persons
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=Activity.ACTIVITY_TYPES)
    confidence_score = models.FloatField()
    location = models.CharField(max_length=255)
    # store raw pose/keypoints for later analysis or visualization
    pose = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
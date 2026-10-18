from django.db import models
from django.utils import timezone
from users.models import CustomUser

class Notification(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    NOTIFICATION_TYPES = (
        ('fall_detected', 'Fall Detected'),
        ('unusual_activity', 'Unusual Activity'),
        ('system_alert', 'System Alert'),
        ('profile_update', 'Profile Update'),
        ('feedback_response', 'Feedback Response'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system_alert')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    activity_context = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class NotificationRule(models.Model):
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=50)
    condition = models.JSONField(default=dict, blank=True)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class AlertLog(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(max_length=20, choices=(
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ))
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Alert for {self.recipient.username} - {self.delivery_status}"
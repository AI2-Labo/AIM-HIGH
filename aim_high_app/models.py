from django.db import models
from django.utils import timezone

class Summary(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    progress = models.IntegerField(default=0)  # Percentage of completion
    
    def __str__(self):
        return self.title

class Concept(models.Model):
    name = models.CharField(max_length=100)
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE, related_name='concepts')
    is_missing = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class ConceptRelationship(models.Model):
    source = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='source_relationships')
    target = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='target_relationships')
    relationship_type = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.source.name} → {self.target.name} ({self.relationship_type})"

class Feedback(models.Model):
    summary = models.OneToOneField(Summary, on_delete=models.CASCADE, related_name='feedback')
    content_quality = models.IntegerField(default=0)  # Scale of 1-5
    feedback_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Feedback for {self.summary.title}"

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender}: {self.message[:30]}..."
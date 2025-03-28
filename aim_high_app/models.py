from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    full_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    bio = models.TextField()
    research_interests = models.TextField()
    personal_background = models.TextField()
    faith_statement = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.full_name

class Class(models.Model):
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='classes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class LearningMaterial(models.Model):
    SOURCE_TYPES = [
        ('online_textbook', 'Online Textbook'),
        ('video', 'Video'),
        ('youtube', 'YouTube Clip'),
        ('file', 'File'),
        ('online_resource', 'Online Resource'),
    ]
    
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='learning_materials')
    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    content_link = models.URLField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class AssignmentType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Assignment(models.Model):
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignment_type = models.ForeignKey(AssignmentType, on_delete=models.CASCADE, related_name='assignments')
    learning_material = models.ForeignKey(LearningMaterial, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class CausalityModel(models.Model):
    MODEL_TYPES = [
        ('explanation', 'Cause-and-Effect Explanation'),
        ('model', 'Cause-and-Effect Model'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='causality_models')
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    content = models.TextField()
    is_reference = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.get_model_type_display()} for {self.assignment.title}"

class CausalityVariable(models.Model):
    model = models.ForeignKey(CausalityModel, on_delete=models.CASCADE, related_name='variables')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class CausalityRelationship(models.Model):
    model = models.ForeignKey(CausalityModel, on_delete=models.CASCADE, related_name='relationships')
    source = models.ForeignKey(CausalityVariable, on_delete=models.CASCADE, related_name='source_relationships')
    target = models.ForeignKey(CausalityVariable, on_delete=models.CASCADE, related_name='target_relationships')
    relationship_type = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.source.name} → {self.target.name}"

# Keep the existing models for chat functionality
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
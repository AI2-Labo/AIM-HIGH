from django.contrib import admin
from .models import (
    InstructorProfile, Class, LearningMaterial, Assignment, AssignmentType,
    CausalityModel, CausalityVariable, CausalityRelationship,
    Summary, Concept, ConceptRelationship, Feedback, ChatMessage
)

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'institution', 'department')
    search_fields = ('full_name', 'institution', 'department')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at')
    list_filter = ('instructor', 'created_at')
    search_fields = ('title', 'description')

@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_type', 'instructor', 'created_at')
    list_filter = ('source_type', 'instructor', 'created_at')
    search_fields = ('title', 'content_link')

@admin.register(AssignmentType)
class AssignmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignment_type', 'instructor', 'created_at')
    list_filter = ('assignment_type', 'instructor', 'created_at')
    search_fields = ('title', 'description')

@admin.register(CausalityModel)
class CausalityModelAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'model_type', 'is_reference', 'created_at')
    list_filter = ('model_type', 'is_reference', 'created_at')
    search_fields = ('content',)

@admin.register(CausalityVariable)
class CausalityVariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'model')
    list_filter = ('model',)
    search_fields = ('name',)

@admin.register(CausalityRelationship)
class CausalityRelationshipAdmin(admin.ModelAdmin):
    list_display = ('source', 'relationship_type', 'target', 'model')
    list_filter = ('model', 'relationship_type')
    search_fields = ('source__name', 'target__name', 'relationship_type')

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'progress')
    list_filter = ('created_at', 'progress')
    search_fields = ('title', 'content', 'summary_text')

@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'summary', 'is_missing')
    list_filter = ('summary', 'is_missing')
    search_fields = ('name',)

@admin.register(ConceptRelationship)
class ConceptRelationshipAdmin(admin.ModelAdmin):
    list_display = ('source', 'relationship_type', 'target')
    search_fields = ('source__name', 'target__name', 'relationship_type')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('summary', 'content_quality', 'created_at')
    list_filter = ('content_quality', 'created_at')
    search_fields = ('feedback_text',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'timestamp', 'summary')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message',)
# aim_high_app/admin.py

from django.contrib import admin
from .models import Summary, Concept, ConceptRelationship, Feedback, ChatMessage

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'progress')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'progress')

@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'summary', 'is_missing')
    search_fields = ('name',)
    list_filter = ('is_missing',)

@admin.register(ConceptRelationship)
class ConceptRelationshipAdmin(admin.ModelAdmin):
    list_display = ('source', 'relationship_type', 'target')
    search_fields = ('relationship_type',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('summary', 'content_quality', 'created_at')
    search_fields = ('feedback_text',)
    list_filter = ('content_quality', 'created_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'timestamp', 'summary')
    search_fields = ('message',)
    list_filter = ('sender', 'timestamp')
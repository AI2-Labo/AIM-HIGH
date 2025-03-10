from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone 
import json
import os

from .models import Summary, Concept, ConceptRelationship, Feedback, ChatMessage
from .utils.openai_utils import get_chatbot_response, generate_summary, extract_concepts, evaluate_summary
from .utils.content_extractor import extract_content_from_url

def index(request):
    # Get active summary ID from session
    active_summary_id = request.session.get('active_summary_id')
    return render(request, 'aim_high_app/index.html', {'active_summary_id': active_summary_id})

def test_css(request):
    """Test route to check if CSS is loading properly"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSS Test</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <h1>CSS Test</h1>
        <p>If this text is styled, CSS is working!</p>
        <div class="primary-button">This should be a styled button</div>
    </body>
    </html>
    """
    return HttpResponse(html)

@csrf_exempt
@require_http_methods(["POST"])
def submit_learning_material(request):
    data = json.loads(request.body)
    url = data.get('url')
    manual_content = data.get('manual_content')
    title = data.get('title')
    
    if url:
        # Extract content from URL
        extracted_data = extract_content_from_url(url)
        title = extracted_data['title'] if not title else title
        content = extracted_data['content']
    else:
        # Use manually entered content
        content = manual_content
    
    if not content:
        return JsonResponse({'error': 'No content provided'}, status=400)
    
    # Create new summary
    summary = Summary.objects.create(
        title=title, 
        content=content, 
        progress=7
    )
    
    # Store the active summary ID in session
    request.session['active_summary_id'] = summary.id
    
    # Create initial chat message
    ChatMessage.objects.create(
        summary=summary,
        sender='assistant',
        message=f"Hey Akshit,\n\nGreat! Once you are ready, Expand the \"Write Your Summary\" section."
    )
    
    return JsonResponse({
        'success': True,
        'summary_id': summary.id,
        'title': title,
        'content_preview': content[:200] + '...' if len(content) > 200 else content
    })

@csrf_exempt
@require_http_methods(["POST"])
def create_summary(request):
    data = json.loads(request.body)
    summary_id = data.get('summary_id') or request.session.get('active_summary_id')
    
    if not summary_id:
        return JsonResponse({'error': 'No active summary session'}, status=400)
    
    try:
        summary = Summary.objects.get(id=summary_id)
    except Summary.DoesNotExist:
        return JsonResponse({'error': 'Summary not found'}, status=404)
    
    # Generate summary using OpenAI
    summary_text = generate_summary(summary.content, summary.title)
    
    # Extract concepts
    concept_data = extract_concepts(summary.content, summary.title)
    
    # Store the summary and update progress
    summary.summary_text = summary_text
    summary.progress = 40
    summary.save()
    
    # Store concepts
    stored_concepts = {}
    for concept_name in concept_data.get('concepts', []):
        concept = Concept.objects.create(
            name=concept_name,
            summary=summary
        )
        stored_concepts[concept_name] = concept.id
    
    # Create relationships
    for rel in concept_data.get('relationships', []):
        source_name = rel.get('source')
        target_name = rel.get('target')
        
        if source_name in stored_concepts and target_name in stored_concepts:
            source_concept = Concept.objects.get(id=stored_concepts[source_name])
            target_concept = Concept.objects.get(id=stored_concepts[target_name])
            
            ConceptRelationship.objects.create(
                source=source_concept,
                target=target_concept,
                relationship_type=rel.get('relationship_type', 'related')
            )
    
    # Add chat message
    ChatMessage.objects.create(
        summary=summary,
        sender='assistant',
        message="Hey Akshit,\n\nIt looks like you've started writing your summary! A tip: you can draft it in a Word file and then copy and paste it into the input box. When you're ready, click the \"Save\" button."
    )
    
    return JsonResponse({
        'success': True,
        'summary_id': summary_id,
        'summary_text': summary_text,
        'concepts': [{'id': stored_concepts[c], 'name': c} for c in stored_concepts]
    })

@csrf_exempt
@require_http_methods(["POST"])
def update_summary(request):
    data = json.loads(request.body)
    summary_id = data.get('summary_id') or request.session.get('active_summary_id')
    summary_text = data.get('summary_text')
    
    if not summary_id:
        return JsonResponse({'error': 'No active summary session'}, status=400)
    
    try:
        summary = Summary.objects.get(id=summary_id)
    except Summary.DoesNotExist:
        return JsonResponse({'error': 'Summary not found'}, status=404)
    
    # Update summary text
    summary.summary_text = summary_text
    summary.progress = 70
    summary.save()
    
    # Add chat message
    ChatMessage.objects.create(
        summary=summary,
        sender='assistant',
        message="Hey Akshit,\nThank you for your submission! Once my review is complete, the feedback section will be activated.\nI'll be back shortly with my feedback on your summary."
    )
    
    return JsonResponse({
        'success': True,
        'summary_id': summary_id
    })

@csrf_exempt
@require_http_methods(["POST"])
def get_summary_feedback(request):
    data = json.loads(request.body)
    summary_id = data.get('summary_id') or request.session.get('active_summary_id')
    
    if not summary_id:
        return JsonResponse({'error': 'No active summary session'}, status=400)
    
    try:
        summary = Summary.objects.get(id=summary_id)
    except Summary.DoesNotExist:
        return JsonResponse({'error': 'Summary not found'}, status=404)
    
    # Evaluate the summary
    evaluation = evaluate_summary(summary.content, summary.summary_text)
    
    # Store feedback
    feedback, created = Feedback.objects.get_or_create(
        summary=summary,
        defaults={
            'content_quality': evaluation.get('score', 3),
            'feedback_text': evaluation.get('feedback', '')
        }
    )
    
    if not created:
        feedback.content_quality = evaluation.get('score', 3)
        feedback.feedback_text = evaluation.get('feedback', '')
        feedback.save()
    
    # Add missing concepts
    for concept_name in evaluation.get('missing_concepts', []):
        Concept.objects.create(
            name=concept_name,
            summary=summary,
            is_missing=True
        )
    
    # Update progress to complete
    summary.progress = 100
    summary.save()
    
    # Add chat message
    ChatMessage.objects.create(
        summary=summary,
        sender='assistant',
        message=f"Here's my feedback on your summary.\n\nYour summary currently has a {evaluation.get('score', 3) * 20}% similarity to the expected model. The knowledge map below represents key ideas and their relationships as structured in your mind. The yellow areas indicate missing components from the expected model, with many key concepts not yet included.\n\nIf you'd like to see the definition of any concept, just type \"show the definition of [concept]\".\nFor examples of how concepts relate to each other, type \"show examples of [concept 1] and [concept 2]\"\n\nAnd if you'd like to learn more about the scoring rubric, feel free to ask!\n\nFinally, and most importantly, to revise your summary, go back to the \"Write Your Summary\" section and click the \"Edit\" button."
    )
    
    # Prepare concepts and relationships for the knowledge map
    concepts = Concept.objects.filter(summary=summary)
    
    # Get relationships
    relationships = []
    for concept in concepts:
        for rel in concept.source_relationships.all():
            relationships.append({
                'source': concept.name,
                'target': rel.target.name,
                'type': rel.relationship_type
            })
    
    missing_concepts = [c.name for c in concepts.filter(is_missing=True)]
    
    return JsonResponse({
        'success': True,
        'summary_id': summary_id,
        'evaluation': {
            'score': evaluation.get('score', 3),
            'feedback': evaluation.get('feedback', ''),
            'concepts': [c.name for c in concepts],
            'missing_concepts': missing_concepts,
            'relationships': relationships
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    data = json.loads(request.body)
    message = data.get('message', '')
    summary_id = data.get('summary_id') or request.session.get('active_summary_id')
    
    # Get summary if available
    summary = None
    if summary_id:
        try:
            summary = Summary.objects.get(id=summary_id)
        except Summary.DoesNotExist:
            pass
    
    # Store user message
    user_message = ChatMessage.objects.create(
        summary=summary,
        sender='user',
        message=message
    )
    
    # Get recent messages for context
    messages = ChatMessage.objects.filter(summary=summary).order_by('-timestamp')[:10]
    messages = list(reversed(messages))  # Get in chronological order
    
    # Get response from OpenAI
    response_text = get_chatbot_response(messages, summary)
    
    # Store assistant response
    assistant_message = ChatMessage.objects.create(
        summary=summary,
        sender='assistant',
        message=response_text
    )
    
    return JsonResponse({
        'success': True,
        'message': response_text,
        'message_id': assistant_message.id
    })

@require_http_methods(["GET"])
def get_chat_history(request):
    summary_id = request.GET.get('summary_id') or request.session.get('active_summary_id')
    
    if summary_id:
        try:
            summary = Summary.objects.get(id=summary_id)
            messages = ChatMessage.objects.filter(summary=summary).order_by('timestamp')
            
            return JsonResponse({
                'success': True,
                'messages': [
                    {
                        'id': msg.id,
                        'sender': msg.sender,
                        'message': msg.message,
                        'timestamp': msg.timestamp.isoformat()
                    }
                    for msg in messages
                ]
            })
        except Summary.DoesNotExist:
            pass
    
    # Return default initial message if no summary or no messages
    return JsonResponse({
        'success': True,
        'messages': [
            {
                'id': 0,
                'sender': 'assistant',
                'message': "Hey Akshit,\nGood morning! I'm Jordan, your personal learning assistant. How's your kitty? She must be adorable! Are you ready to start the summarization assignment? If you haven't read the article yet, you can start with the \"Learning Material\" section. Let me know if you have any questions about the topic.",
                'timestamp': timezone.now().isoformat()
            }
        ]
    })

@require_http_methods(["GET"])
def get_summary_data(request):
    summary_id = request.GET.get('summary_id') or request.session.get('active_summary_id')
    
    if not summary_id:
        return JsonResponse({'error': 'No active summary session'}, status=400)
    
    try:
        summary = Summary.objects.get(id=summary_id)
    except Summary.DoesNotExist:
        return JsonResponse({'error': 'Summary not found'}, status=404)
    
    # Get concepts
    concepts = Concept.objects.filter(summary=summary)
    
    concept_data = []
    for concept in concepts:
        concept_data.append({
            'id': concept.id,
            'name': concept.name,
            'is_missing': concept.is_missing
        })
    
    # Get relationships
    relationships = []
    for concept in concepts:
        for rel in concept.source_relationships.all():
            relationships.append({
                'source': concept.name,
                'target': rel.target.name,
                'type': rel.relationship_type
            })
    
    # Get feedback if available
    feedback_data = None
    try:
        feedback = summary.feedback
        feedback_data = {
            'content_quality': feedback.content_quality,
            'feedback_text': feedback.feedback_text
        }
    except Feedback.DoesNotExist:
        pass
    
    return JsonResponse({
        'success': True,
        'summary': {
            'id': summary.id,
            'title': summary.title,
            'content': summary.content,
            'summary_text': summary.summary_text or '',
            'progress': summary.progress,
            'created_at': summary.created_at.isoformat(),
            'updated_at': summary.updated_at.isoformat()
        },
        'concepts': concept_data,
        'relationships': relationships,
        'feedback': feedback_data
    })
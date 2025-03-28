from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
import json
import os

from .models import (
    Summary, Concept, ConceptRelationship, Feedback, ChatMessage,
    InstructorProfile, Class, LearningMaterial, Assignment, AssignmentType,
    CausalityModel, CausalityVariable, CausalityRelationship
)
from .utils.openai_utils import get_chatbot_response, generate_summary, extract_concepts, evaluate_summary
from .utils.content_extractor import extract_content_from_url

def index(request):
    """Home page view"""
    return render(request, 'aim_high_app/index.html')

def custom_login(request):
    """Custom login view"""
    return LoginView.as_view(template_name='registration/login.html')(request)

@login_required
def instructor_profile(request):
    """View for instructor profile page"""
    # For demo purposes, get or create the first instructor profile
    instructor, created = InstructorProfile.objects.get_or_create(
        defaults={
            'full_name': 'Dr. Min Kyu Kim',
            'title': 'Associate Professor',
            'institution': 'Georgia State University',
            'department': 'Learning Sciences',
            'bio': 'Founding director of the AI² Research Laboratory. My research focuses on AI-driven personalized learning, technology-enhanced assessment, and learner engagement in digital environments.',
            'research_interests': 'AI in education, learning analytics, educational technology',
            'personal_background': 'I was born and raised in Korea before pursuing my graduate studies in the United States.',
            'faith_statement': 'Faith is an important part of my life, and as a sincere Christian, I strive to live by values of integrity, kindness, and purpose.'
        }
    )
    
    return render(request, 'aim_high_app/profile.html', {'instructor': instructor})

@login_required
def my_classes(request):
    """View for instructor's classes"""
    # For demo purposes, get the first instructor
    instructor = InstructorProfile.objects.first()
    classes = Class.objects.filter(instructor=instructor)
    
    return render(request, 'aim_high_app/classes.html', {'classes': classes})

@login_required
def learning_materials(request):
    """View for learning materials management"""
    # For demo purposes, get the first instructor
    instructor = InstructorProfile.objects.first()
    materials = LearningMaterial.objects.filter(instructor=instructor)
    
    return render(request, 'aim_high_app/learning_materials.html', {'materials': materials})

@login_required
def learning_material_management(request, material_id=None):
    """View for adding/editing learning material"""
    # For demo purposes, get the first instructor
    instructor = InstructorProfile.objects.first()
    
    if material_id:
        material = get_object_or_404(LearningMaterial, id=material_id, instructor=instructor)
    else:
        material = None
    
    source_types = LearningMaterial.SOURCE_TYPES
    
    return render(request, 'aim_high_app/learning_material_management.html', {
        'material': material,
        'source_types': source_types
    })

@login_required
def assignments(request, assignment_type=None):
    """View for assignments"""
    # For demo purposes, get the first instructor
    instructor = InstructorProfile.objects.first()
    
    if assignment_type and assignment_type != 'All':
        assignment_type_obj = get_object_or_404(AssignmentType, name=assignment_type)
        assignments = Assignment.objects.filter(
            instructor=instructor, 
            assignment_type=assignment_type_obj
        )
    else:
        assignments = Assignment.objects.filter(instructor=instructor)
        
    assignment_types = AssignmentType.objects.all()
    
    return render(request, 'aim_high_app/assignments.html', {
        'assignments': assignments,
        'assignment_types': assignment_types,
        'current_type': assignment_type
    })

@login_required
def causality_analysis(request, assignment_id=None):
    """View for causality analysis assignment"""
    # For demo purposes, get the first instructor
    instructor = InstructorProfile.objects.first()
    
    if assignment_id:
        assignment = get_object_or_404(Assignment, id=assignment_id, instructor=instructor)
    else:
        assignment = None
    
    materials = LearningMaterial.objects.filter(instructor=instructor)
    
    # Get existing causality models if assignment exists
    causality_models = []
    if assignment:
        causality_models = CausalityModel.objects.filter(assignment=assignment)
    
    return render(request, 'aim_high_app/causality_analysis.html', {
        'assignment': assignment,
        'materials': materials,
        'causality_models': causality_models
    })

@csrf_exempt
def save_learning_material(request):
    """API endpoint to save learning material"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # For demo purposes, get the first instructor
            instructor = InstructorProfile.objects.first()
            
            title = data.get('title')
            source_type = data.get('source_type')
            content_link = data.get('content_link')
            
            material_id = data.get('material_id')
            
            if not title or not source_type or not content_link:
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            if material_id:
                # Update existing material
                try:
                    material = LearningMaterial.objects.get(id=material_id, instructor=instructor)
                    material.title = title
                    material.source_type = source_type
                    material.content_link = content_link
                    material.save()
                except LearningMaterial.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Material not found'})
            else:
                # Create new material
                material = LearningMaterial.objects.create(
                    instructor=instructor,
                    title=title,
                    source_type=source_type,
                    content_link=content_link
                )
            
            return JsonResponse({
                'success': True,
                'material_id': material.id,
                'message': 'Learning material saved successfully'
            })
        except Exception as e:
            print(f"Error saving learning material: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_learning_material(request, material_id):
    """API endpoint to delete learning material"""
    if request.method == 'POST':
        try:
            # For demo purposes, get the first instructor
            instructor = InstructorProfile.objects.first()
            
            material = get_object_or_404(LearningMaterial, id=material_id, instructor=instructor)
            material.delete()
            
            return JsonResponse({'success': True, 'message': 'Learning material deleted successfully'})
        except Exception as e:
            print(f"Error deleting learning material: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def save_causality_model(request):
    """API endpoint to save causality model"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # For demo purposes, get the first instructor
            instructor = InstructorProfile.objects.first()
            
            assignment_id = data.get('assignment_id')
            model_type = data.get('model_type')
            content = data.get('content')
            is_reference = data.get('is_reference', False)
            
            if assignment_id:
                try:
                    assignment = Assignment.objects.get(id=assignment_id, instructor=instructor)
                except Assignment.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Assignment not found'})
            else:
                # Create new assignment if needed
                material_id = data.get('material_id')
                title = data.get('title')
                
                if not material_id or not title:
                    return JsonResponse({'success': False, 'error': 'Missing required fields'})
                
                try:
                    material = LearningMaterial.objects.get(id=material_id, instructor=instructor)
                except LearningMaterial.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Learning material not found'})
                
                assignment_type, _ = AssignmentType.objects.get_or_create(name='Causality Analysis')
                
                assignment = Assignment.objects.create(
                    instructor=instructor,
                    title=title,
                    description='',
                    assignment_type=assignment_type,
                    learning_material=material
                )
            
            # Create the causality model
            causality_model = CausalityModel.objects.create(
                assignment=assignment,
                model_type=model_type,
                content=content,
                is_reference=is_reference
            )
            
            # Process variables and relationships if provided
            variables = data.get('variables', [])
            relationships = data.get('relationships', [])
            
            variable_map = {}
            for var_name in variables:
                variable = CausalityVariable.objects.create(
                    model=causality_model,
                    name=var_name
                )
                variable_map[var_name] = variable
            
            for rel in relationships:
                source_name = rel.get('source')
                target_name = rel.get('target')
                rel_type = rel.get('type', '')
                
                if source_name in variable_map and target_name in variable_map:
                    CausalityRelationship.objects.create(
                        model=causality_model,
                        source=variable_map[source_name],
                        target=variable_map[target_name],
                        relationship_type=rel_type
                    )
            
            return JsonResponse({
                'success': True,
                'model_id': causality_model.id,
                'assignment_id': assignment.id,
                'message': 'Causality model saved successfully'
            })
        except Exception as e:
            print(f"Error saving causality model: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def create_assignment(request):
    """API endpoint to create new assignment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # For demo purposes, get the first instructor
            instructor = InstructorProfile.objects.first()
            
            title = data.get('title')
            assignment_type_name = data.get('assignment_type')
            material_id = data.get('material_id')
            description = data.get('description', '')
            
            if not title or not assignment_type_name or not material_id:
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            try:
                material = LearningMaterial.objects.get(id=material_id, instructor=instructor)
            except LearningMaterial.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Learning material not found'})
            
            assignment_type, _ = AssignmentType.objects.get_or_create(name=assignment_type_name)
            
            assignment = Assignment.objects.create(
                instructor=instructor,
                title=title,
                description=description,
                assignment_type=assignment_type,
                learning_material=material
            )
            
            return JsonResponse({
                'success': True,
                'assignment_id': assignment.id,
                'message': 'Assignment created successfully'
            })
        except Exception as e:
            print(f"Error creating assignment: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_assignment(request, assignment_id):
    """API endpoint to delete assignment"""
    if request.method == 'POST':
        try:
            # For demo purposes, get the first instructor
            instructor = InstructorProfile.objects.first()
            
            assignment = get_object_or_404(Assignment, id=assignment_id, instructor=instructor)
            assignment.delete()
            
            return JsonResponse({'success': True, 'message': 'Assignment deleted successfully'})
        except Exception as e:
            print(f"Error deleting assignment: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Chat functionality
@csrf_exempt
def chat(request):
    """API endpoint for chat messages"""
    if request.method == 'POST':
        try:
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
        except Exception as e:
            print(f"Error in chat: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_chat_history(request):
    """API endpoint to get chat history"""
    try:
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
                    'message': "Hey Min,\nHow are you this afternoon? Do you want to create a causality analysis assignment?",
                    'timestamp': timezone.now().isoformat()
                }
            ]
        })
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

# Additional utility views
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

def submit_learning_material(request):
    """API endpoint to submit learning material"""
    if request.method == 'POST':
        try:
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
                message=f"Hey Min,\n\nGreat! Once you are ready, Expand the \"Write Your Summary\" section."
            )
            
            return JsonResponse({
                'success': True,
                'summary_id': summary.id,
                'title': title,
                'content_preview': content[:200] + '...' if len(content) > 200 else content
            })
        except Exception as e:
            print(f"Error submitting learning material: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def create_summary(request):
    """API endpoint to create summary"""
    if request.method == 'POST':
        try:
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
                message="Hey Min,\n\nIt looks like you've started writing your summary! A tip: you can draft it in a Word file and then copy and paste it into the input box. When you're ready, click the \"Save\" button."
            )
            
            return JsonResponse({
                'success': True,
                'summary_id': summary_id,
                'summary_text': summary_text,
                'concepts': [{'id': stored_concepts[c], 'name': c} for c in stored_concepts]
            })
        except Exception as e:
            print(f"Error creating summary: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def update_summary(request):
    """API endpoint to update summary"""
    if request.method == 'POST':
        try:
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
                message="Hey Min,\nThank you for your submission! Once my review is complete, the feedback section will be activated.\nI'll be back shortly with my feedback on your summary."
            )
            
            return JsonResponse({
                'success': True,
                'summary_id': summary_id
            })
        except Exception as e:
            print(f"Error updating summary: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_summary_feedback(request):
    """API endpoint to get summary feedback"""
    if request.method == 'POST':
        try:
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
        except Exception as e:
            print(f"Error getting summary feedback: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_summary_data(request):
    """API endpoint to get summary data"""
    try:
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
                'summary_text': summary.summary_text if hasattr(summary, 'summary_text') else '',
                'progress': summary.progress,
            'created_at': summary.created_at.isoformat(),
                'updated_at': summary.updated_at.isoformat()
            },
            'concepts': concept_data,
            'relationships': relationships,
            'feedback': feedback_data
        })
    except Exception as e:
        print(f"Error getting summary data: {e}")
        return JsonResponse({'error': str(e)}, status=500)
            
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

@csrf_exempt
def update_profile(request):
    """API endpoint to update instructor profile"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # For demo purposes, get the first instructor
            instructor = InstructorProfile.objects.first()
            
            if not instructor:
                return JsonResponse({'success': False, 'error': 'Instructor profile not found'})
            
            # Update the fields from the request
            if 'full_name' in data:
                instructor.full_name = data['full_name']
            if 'title' in data:
                instructor.title = data['title']
            if 'institution' in data:
                instructor.institution = data['institution']
            if 'bio' in data:
                instructor.bio = data['bio']
            
            # Save changes
            instructor.save()
            
            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
        except Exception as e:
            print(f"Error updating profile: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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
    
    # Get learning materials for modal
    materials = LearningMaterial.objects.filter(instructor=instructor)
    
    return render(request, 'aim_high_app/assignments.html', {
        'assignments': assignments,
        'assignment_types': assignment_types,
        'current_type': assignment_type,
        'materials': materials
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
            auto_generate = data.get('auto_generate', False)
            
            # Get assignment
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
            
            # If auto_generate is True, use AI to generate the causality model
            variables = data.get('variables', [])
            relationships = data.get('relationships', [])
            
            if auto_generate and assignment.learning_material:
                # Use the learning material content to generate causality model
                material_content = assignment.learning_material.content_link
                
                # Extract the content from the URL
                extracted_data = extract_content_from_url(material_content)
                material_text = extracted_data.get('content', '')
                material_title = extracted_data.get('title', assignment.title)
                
                # Analyze causal relationships
                analysis_result = analyze_causal_relationships(material_text, material_title)
                
                # Use the generated summary as content if not provided
                if not content and 'summary' in analysis_result:
                    content = analysis_result.get('summary', '')
                
                # Use generated variables and relationships if not provided
                if not variables and 'concepts' in analysis_result:
                    variables = analysis_result.get('concepts', [])
                
                if not relationships and 'relationships' in analysis_result:
                    relationships = analysis_result.get('relationships', [])
            
            # Create the causality model
            causality_model = CausalityModel.objects.create(
                assignment=assignment,
                model_type=model_type,
                content=content,
                is_reference=is_reference
            )
            
            # Process variables and relationships
            variable_map = {}
            for var_name in variables:
                variable = CausalityVariable.objects.create(
                    model=causality_model,
                    name=var_name
                )
                variable_map[var_name] = variable
            
            for rel in relationships:
                if isinstance(rel, dict):
                    source_name = rel.get('source', '')
                    target_name = rel.get('target', '')
                    rel_type = rel.get('relationship_type', rel.get('type', ''))
                elif isinstance(rel, str):
                    # Parse string relationship in case it's in the format "A -> B"
                    if "->" in rel:
                        source_name, target_name = [s.strip() for s in rel.split("->")]
                        rel_type = "causes"
                    elif "<-" in rel:
                        target_name, source_name = [s.strip() for s in rel.split("<-")]
                        rel_type = "caused by"
                    elif "<->" in rel:
                        source_name, target_name = [s.strip() for s in rel.split("<->")]
                        rel_type = "bidirectional"
                    else:
                        continue  # Skip if format not recognized
                else:
                    continue  # Skip if not a dict or string
                
                # Create variables if they don't exist yet
                if source_name and source_name not in variable_map:
                    source_var = CausalityVariable.objects.create(
                        model=causality_model,
                        name=source_name
                    )
                    variable_map[source_name] = source_var
                
                if target_name and target_name not in variable_map:
                    target_var = CausalityVariable.objects.create(
                        model=causality_model,
                        name=target_name
                    )
                    variable_map[target_name] = target_var
                
                # Create relationship if both variables exist
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
            context = data.get('context', {})
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
            
            # Context-aware response (simplified version - would normally use AI)
            page_context = context.get('name', '')
            url_path = context.get('url', '')
            
            # Determine response based on context and message
            if 'profile' in url_path:
                response_text = get_chatbot_response(messages, summary)
            elif 'learning-material' in url_path:
                response_text = get_chatbot_response(messages, summary)
            elif 'causality-analysis' in url_path:
                response_text = get_chatbot_response(messages, summary)
            elif 'assignments' in url_path:
                response_text = get_chatbot_response(messages, summary)
            elif 'test' in url_path:
                response_text = get_chatbot_response(messages, summary)
            else:
                # Use OpenAI for general responses
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


# Add these new functions to your existing views.py file

def test_evaluation(request):
    """View for the student test/evaluation page"""
    return render(request, 'aim_high_app/test_evaluation.html')

@csrf_exempt
def evaluate_student_summary(request):
    """API endpoint to evaluate student summary using OpenAI-powered analysis"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_summary = data.get('summary', '')
            
            if not student_summary:
                return JsonResponse({'error': 'No summary provided'}, status=400)
            
            # Expert model for comparison
            expert_model = """Eukaryotic cells are distinguished by their complex nuclear membrane and presence of membrane-bound organelles in the cytoplasm. These organelles include mitochondria, endoplasmic reticulum, Golgi apparatus, lysosomes, and peroxisomes, which are organized by the cytoskeleton. The cytoskeleton maintains cell shape and directs intracellular transport. Unlike prokaryotic cells with circular chromosomes, eukaryotic cells have multiple rod-shaped chromosomes for their genome."""
            
            # Get an in-depth evaluation using our OpenAI function
            evaluation_result = evaluate_summary(expert_model, student_summary)
            
            # Calculate similarity score
            similarity_score = calculate_similarity(student_summary, expert_model)
            
            # Determine star rating
            stars = 1
            if similarity_score > 90:
                stars = 5
            elif similarity_score > 70:
                stars = 4
            elif similarity_score > 50:
                stars = 3
            elif similarity_score > 30:
                stars = 2
            
            # Get feedback from the evaluation
            feedback = evaluation_result.get('feedback', '')
            
            # If feedback has both strengths and areas for improvement, split them
            if ' improve' in feedback.lower() or 'could be' in feedback.lower():
                # Try to split into strength and improvement
                parts = feedback.split('. ', 1)
                if len(parts) > 1:
                    feedback = parts[0]
                    improvement = parts[1]
                else:
                    # Default to generated feedback if we can't split nicely
                    feedback, improvement = generate_feedback(similarity_score)
            else:
                # Default to generated feedback if there's no clear improvement part
                feedback, improvement = generate_feedback(similarity_score)
            
            # Get missing concepts from the evaluation
            missing_concepts = evaluation_result.get('missing_concepts', [])
            
            # If we don't have missing concepts from the API, generate them
            if not missing_concepts:
                missing_concepts = get_missing_concepts(student_summary)
            
            # Get present concepts from the evaluation
            present_concepts = evaluation_result.get('present_concepts', [])
            
            return JsonResponse({
                'success': True,
                'similarity_score': similarity_score,
                'stars': stars,
                'feedback': feedback,
                'improvement': improvement,
                'missing_concepts': missing_concepts,
                'present_concepts': present_concepts,
                'evaluation': evaluation_result
            })
        except Exception as e:
            print(f"Error evaluating student summary: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def calculate_similarity(text1, text2):
    """
    Calculate similarity between student text and expert model using our improved OpenAI-based evaluation
    """
    # Call the OpenAI evaluation function
    evaluation = evaluate_summary(text2, text1)  # original content, student summary
    
    # Get the score from the evaluation (on a scale of 1-5)
    score_1_to_5 = evaluation.get("score", 3)
    
    # Convert to a percentage (1-5 → 0-100%)
    percentage_score = (score_1_to_5 / 5) * 100
    
    # Get missing and present concepts
    missing_concepts = evaluation.get("missing_concepts", [])
    present_concepts = evaluation.get("present_concepts", [])
    
    # Calculate a concept coverage component (what percentage of concepts are covered)
    all_concepts = missing_concepts + present_concepts
    if all_concepts:
        concept_coverage = (len(present_concepts) / len(all_concepts)) * 100
    else:
        concept_coverage = 0
    
    # Blend the AI-provided score with the concept coverage for a final score
    final_score = int((percentage_score * 0.7) + (concept_coverage * 0.3))
    
    # Store the evaluation data in a session variable for later use
    return max(5, min(100, final_score))  # Ensure score is between 5-100%

def generate_feedback(score):
    """Generate feedback based on similarity score"""
    # The feedback is now generated by the OpenAI evaluation
    # We'll provide generic feedback here as fallback
    if score < 30:
        feedback = "Your summary captures only a few key points and lacks completeness."
        improvement = "Focus on including the main characteristics of eukaryotic cells: nuclear membrane, membrane-bound organelles, cytoskeleton, and chromosome structure."
    elif score < 50:
        feedback = "Your summary includes some important concepts but misses several key details."
        improvement = "Add more specific information about the types of organelles and the role of the cytoskeleton in cell organization."
    elif score < 70:
        feedback = "Your summary covers many important aspects of eukaryotic cells but could be more comprehensive."
        improvement = "Consider adding details about how organelles are organized and the difference in chromosome structure compared to prokaryotes."
    elif score < 90:
        feedback = "Your summary is good and covers most key characteristics accurately."
        improvement = "To further improve, ensure you mention all the specific organelles and their organization by the cytoskeleton."
    else:
        feedback = "Excellent summary that comprehensively covers all key characteristics of eukaryotic cells."
        improvement = "Your summary effectively captures all the essential information with clarity and accuracy."
    
    return feedback, improvement

def get_missing_concepts(summary_text):
    """
    Get missing concepts based on real-time analysis of the summary
    """
    # Define the expert model content for eukaryotic cells
    expert_model = """Eukaryotic cells are characterized by a complex nuclear membrane. Also, eukaryotic cells are characterized by the presence of membrane-bound organelles in the cytoplasm. Organelles such as mitochondria, the endoplasmic reticulum (ER), Golgi apparatus, lysosomes, and peroxisomes are held in place by the cytoskeleton, an internal network that directs transport of intracellular components and helps maintain cell shape (Figure 3.35). The genome of eukaryotic cells is packaged in multiple, rod-shaped chromosomes as opposed to the single, circular-shaped chromosome that characterizes most prokaryotic cells."""
    
    # Use the OpenAI evaluation to get missing concepts
    evaluation = evaluate_summary(expert_model, summary_text)
    
    # Return the missing concepts from the evaluation
    return evaluation.get("missing_concepts", [])
    
def analyze_causal_relationships(content, title):
    """
    Analyze text to extract causal relationships between concepts
    Uses the improved prompt from coworkers
    """
    # This now uses the enhanced extract_concepts function with the improved prompt
    result = extract_concepts(content, title)
    
    # Return the structured result with concepts, relationships and summary
    return result
    
@csrf_exempt
def extract_preview(request):
    """API endpoint to extract content from a learning material or URL"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            material_id = data.get('material_id')
            url = data.get('url')
            
            if not material_id and not url:
                return JsonResponse({'success': False, 'error': 'Either material_id or URL must be provided'})
            
            # Get content from material if material_id is provided
            if material_id:
                try:
                    # For demo purposes, get the first instructor
                    instructor = InstructorProfile.objects.first()
                    material = get_object_or_404(LearningMaterial, id=material_id, instructor=instructor)
                    content_link = material.content_link
                    
                    # Extract content from the content_link
                    extracted_data = extract_content_from_url(content_link)
                    
                    return JsonResponse({
                        'success': True,
                        'title': extracted_data.get('title', material.title),
                        'content': extracted_data.get('content', ''),
                        'material_id': material_id
                    })
                    
                except Exception as e:
                    print(f"Error extracting content from material: {e}")
                    return JsonResponse({'success': False, 'error': str(e)})
            
            # Extract content directly from URL if provided
            elif url:
                extracted_data = extract_content_from_url(url)
                
                return JsonResponse({
                    'success': True,
                    'title': extracted_data.get('title', 'Extracted Content'),
                    'content': extracted_data.get('content', ''),
                    'url': url
                })
                
        except Exception as e:
            print(f"Error in extract_preview: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
@csrf_exempt
def extract_preview(request):
    """API endpoint to extract content from a learning material or URL"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            material_id = data.get('material_id')
            url = data.get('url')
            
            if not material_id and not url:
                return JsonResponse({'success': False, 'error': 'Either material_id or URL must be provided'})
            
            # Get content from material if material_id is provided
            if material_id:
                try:
                    # For demo purposes, get the first instructor
                    instructor = InstructorProfile.objects.first()
                    material = get_object_or_404(LearningMaterial, id=material_id, instructor=instructor)
                    content_link = material.content_link
                    
                    # Extract content from the content_link
                    extracted_data = extract_content_from_url(content_link)
                    
                    return JsonResponse({
                        'success': True,
                        'title': extracted_data.get('title', material.title),
                        'content': extracted_data.get('content', ''),
                        'material_id': material_id
                    })
                    
                except Exception as e:
                    print(f"Error extracting content from material: {e}")
                    return JsonResponse({'success': False, 'error': str(e)})
            
            # Extract content directly from URL if provided
            elif url:
                extracted_data = extract_content_from_url(url)
                
                return JsonResponse({
                    'success': True,
                    'title': extracted_data.get('title', 'Extracted Content'),
                    'content': extracted_data.get('content', ''),
                    'url': url
                })
                
        except Exception as e:
            print(f"Error in extract_preview: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
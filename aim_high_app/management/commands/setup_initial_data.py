from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from aim_high_app.models import (
    InstructorProfile, Class, LearningMaterial, 
    AssignmentType, Assignment, CausalityModel
)

class Command(BaseCommand):
    help = 'Set up initial data for the AIM HIGH application'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create a test user if not exists
        if not User.objects.filter(username='instructor').exists():
            user = User.objects.create_user(
                username='instructor',
                email='instructor@example.com',
                password='password123'
            )
            self.stdout.write(self.style.SUCCESS('Created test user: instructor'))
        else:
            user = User.objects.get(username='instructor')
            self.stdout.write('Test user already exists')
        
        # Create an instructor profile
        instructor, created = InstructorProfile.objects.get_or_create(
            user=user,
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
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created instructor profile'))
        else:
            self.stdout.write('Instructor profile already exists')
        
        # Create assignment types
        assignment_types = [
            'Summarization', 
            'Causality Analysis', 
            'Solution Explanation', 
            'Argumentation', 
            'Creative Writing'
        ]
        
        for type_name in assignment_types:
            AssignmentType.objects.get_or_create(name=type_name)
        
        self.stdout.write(self.style.SUCCESS('Created assignment types'))
        
        # Create learning materials
        materials = [
            {
                'title': '3.4 Unique Characteristics of Eukaryotic Cells',
                'source_type': 'online_textbook',
                'content_link': 'https://openstax.org/books/microbiology/pages/3-4-unique-characteristics-of-eukaryotic-cells'
            },
            {
                'title': '4.1 Motion and Forces',
                'source_type': 'online_textbook',
                'content_link': 'https://openstax.org/books/physics/pages/4-1-motion-and-forces'
            }
        ]
        
        for material_data in materials:
            material, created = LearningMaterial.objects.get_or_create(
                instructor=instructor,
                title=material_data['title'],
                defaults={
                    'source_type': material_data['source_type'],
                    'content_link': material_data['content_link']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created learning material: {material.title}"))
            else:
                self.stdout.write(f"Learning material already exists: {material.title}")
        
        # Create sample assignments
        causality_type = AssignmentType.objects.get(name='Causality Analysis')
        summarization_type = AssignmentType.objects.get(name='Summarization')
        
        physics_material = LearningMaterial.objects.get(title='4.1 Motion and Forces')
        biology_material = LearningMaterial.objects.get(title='3.4 Unique Characteristics of Eukaryotic Cells')
        
        # Causality Analysis assignment
        causality_assignment, created = Assignment.objects.get_or_create(
            instructor=instructor,
            title='Forces and Motion Causality',
            assignment_type=causality_type,
            defaults={
                'description': 'Analyzing causal relationships in forces and motion',
                'learning_material': physics_material
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created assignment: {causality_assignment.title}"))
            
            # Create reference models
            explanation_model = CausalityModel.objects.create(
                assignment=causality_assignment,
                model_type='explanation',
                content='Forces are the driving factor behind motion. Forces are essentially pushes or pulls that cause objects to move. By conducting experiments with a hacksaw blade and a truck, the concept of forces and their effects on motion is explored. When a constant force is applied to an object, it results in a constant acceleration. Increasing the force leads to a larger acceleration, while increasing the mass of the object results in a smaller acceleration. Forces are interactions between two objects, with every force having an agent that causes the force. Forces can be contact forces, which act on an object by touching it, or long-range forces, which act without physical contact.',
                is_reference=True
            )
            
            model_model = CausalityModel.objects.create(
                assignment=causality_assignment,
                model_type='model',
                content='Causal model showing relationships between Force, Motion, Acceleration, Mass, and Newton\'s Laws',
                is_reference=True
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created causality models for assignment"))
        else:
            self.stdout.write(f"Assignment already exists: {causality_assignment.title}")
        
        # Summarization assignment
        summary_assignment, created = Assignment.objects.get_or_create(
            instructor=instructor,
            title='Eukaryotic Cells Summarization',
            assignment_type=summarization_type,
            defaults={
                'description': 'Summarize the key characteristics of eukaryotic cells',
                'learning_material': biology_material
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created assignment: {summary_assignment.title}"))
        else:
            self.stdout.write(f"Assignment already exists: {summary_assignment.title}")
        
        self.stdout.write(self.style.SUCCESS('All initial data has been set up!'))
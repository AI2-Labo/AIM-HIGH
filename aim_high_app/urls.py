from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test-css/', views.test_css, name='test_css'),
    
    # Instructor panel routes
    path('profile/', views.instructor_profile, name='profile'),
    path('classes/', views.my_classes, name='classes'),
    path('learning-materials/', views.learning_materials, name='learning_materials'),
    path('learning-material/manage/<int:material_id>/', views.learning_material_management, name='manage_learning_material'),
    path('learning-material/manage/', views.learning_material_management, name='new_learning_material'),
    
    # Assignment routes
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<str:assignment_type>/', views.assignments, name='assignments_by_type'),
    path('assignments/causality-analysis/<int:assignment_id>/', views.causality_analysis, name='edit_causality_analysis'),
    path('assignments/causality-analysis/', views.causality_analysis, name='new_causality_analysis'),
    
    # API routes
    path('api/learning-material', views.submit_learning_material, name='submit_learning_material'),
    path('api/generate-summary', views.create_summary, name='create_summary'),
    path('api/update-summary', views.update_summary, name='update_summary'),
    path('api/evaluate-summary', views.get_summary_feedback, name='get_summary_feedback'),
    path('api/chat', views.chat, name='chat'),
    path('api/get-chat-history', views.get_chat_history, name='get_chat_history'),
    path('api/get-summary-data', views.get_summary_data, name='get_summary_data'),
    path('api/save-learning-material', views.save_learning_material, name='save_learning_material'),
    path('api/delete-learning-material/<int:material_id>/', views.delete_learning_material, name='delete_learning_material'),
    path('api/create-assignment', views.create_assignment, name='create_assignment'),
    path('api/delete-assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('api/save-causality-model', views.save_causality_model, name='save_causality_model'),
]
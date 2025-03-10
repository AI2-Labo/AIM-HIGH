# aim_high_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test-css/', views.test_css, name='test_css'),
    path('api/learning-material', views.submit_learning_material, name='submit_learning_material'),
    path('api/generate-summary', views.create_summary, name='create_summary'),
    path('api/update-summary', views.update_summary, name='update_summary'),
    path('api/evaluate-summary', views.get_summary_feedback, name='get_summary_feedback'),
    path('api/chat', views.chat, name='chat'),
    path('api/get-chat-history', views.get_chat_history, name='get_chat_history'),
    path('api/get-summary-data', views.get_summary_data, name='get_summary_data'),
]
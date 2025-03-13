# aim_high_app/utils/openai_utils.py
import json

from ollama import Client
import os
from django.conf import settings
from . import constants

client = Client(settings.OLLAMA_HOST_URL)


def get_chatbot_response(messages, summary=None, response_format=constants.BaseJson):
    """
    Get response from Llama based on the conversation history
    """
    # Prepare the system message based on summary content if available
    system_content = "You are Jordan, a personal learning assistant. Your role is to help students summarize academic content and identify key concepts and relationships between them. Be supportive, encouraging, and provide constructive feedback."
    
    if summary:
        system_content += f"\n\nThe student is working on summarizing the following topic: {summary.title}"
    
    # Format the conversation for Llama
    formatted_messages = [
        {"role": "system", "content": system_content}
    ]
    
    # Add the conversation history
    for msg in messages:
        role = "user" if msg.sender == "user" else "assistant"
        formatted_messages.append({"role": role, "content": msg.message})
    
    # Get response from Llama
    try:
        """
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=formatted_messages,
            max_tokens=500,
            temperature=0.7,
        )"""

        response = client.chat(
            model="llama3.3:latest",
            messages=formatted_messages,
            format=response_format.model_json_schema()
        )

        assistant_response = response['message']['content']
        response_dict = json.loads(assistant_response)
        parsed_response = response_dict["message"]

        return parsed_response
    except Exception as e:
        print(f"Error calling Llama API: {e}")
        return "I'm having trouble connecting right now. Please try again later."

def generate_summary(content, title, response_format=constants.BaseJson): # Should be replaced with Vanorah's code
    """
    Generate a summary of the provided content
    """
    try:
        response = client.chat(
            model="llama3.3:latest",
            messages=[
                {"role": "system", "content": "You are an academic summarization assistant. Create a concise summary of the following content, highlighting the key concepts and their relationships. Your summary must be substantive and focused on the key information."},
                {"role": "user", "content": f"Title: {title}\n\nContent: {content}\n\nPlease provide a summary in 3-4 paragraphs."}
            ],
            format=response_format.model_json_schema()
        )

        assistant_response = response['message']['content']
        response_dict = json.loads(assistant_response)
        parsed_response = response_dict["message"]

        return parsed_response
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Unable to generate summary at this time."

def extract_concepts(content, title, response_format=constants.BaseJson): # Should be replaced with Briana's code
    """
    Extract key concepts from the content
    """
    try:
        response = client.chat(
            model="llama3.3:latest",
            messages=[
                {"role": "system", "content": "You are a concept extraction assistant. Extract key concepts from the given content and identify relationships between them."},
                {"role": "user", "content": f"Title: {title}\n\nContent: {content}\n\nPlease extract key concepts and their relationships. Format your response as JSON with 'concepts' as a list of concept names and 'relationships' as a list of objects with 'source', 'target', and 'relationship_type' properties. The concepts should contain ONLY the names of the concepts, do not put any description."}
            ],
            format=response_format.model_json_schema()
        )

        assistant_response = response['message']['content']
        response_dict = json.loads(assistant_response)

        return response_dict

    except Exception as e:
        print(f"Error extracting concepts: {e}")
        return {"concepts": [], "relationships": []}

def evaluate_summary(original_content, summary_content, response_format=constants.EvaluateSummaryFeedback):
    """
    Evaluate the quality of a summary compared to the original content
    """
    try:
        response = client.chat(
            model="llama3.3:latest",
            messages=[
                {"role": "system", "content": "You are a summary evaluation assistant. Evaluate the quality of a summary compared to the original content."},
                {"role": "user", "content": f"Original content: {original_content}\n\nSummary: {summary_content}\n\nPlease evaluate the summary on a scale of 1-5 for content quality, accuracy, and completeness. Also identify any key concepts that are missing in the summary. Format your response as JSON with 'score', 'feedback', and 'missing_concepts' properties. The concepts should contain ONLY the names of the concepts, do not put any description."}
            ],
            format=response_format.model_json_schema()
        )

        assistant_response = response['message']['content']
        response_dict = json.loads(assistant_response)

        return response_dict

    except Exception as e:
        print(f"Error evaluating summary: {e}")
        return {"score": 0, "feedback": "Error evaluating summary", "missing_concepts": []}
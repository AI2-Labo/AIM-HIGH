# aim_high_app/utils/openai_utils.py

import openai
import json
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def get_chatbot_response(messages, summary=None):
    """
    Get response from OpenAI based on the conversation history
    """
    # Prepare the system message based on summary content if available
    system_content = "You are Jordan, a personal learning assistant. Your role is to help students summarize academic content and identify key concepts and relationships between them. Be supportive, encouraging, and provide constructive feedback."
    
    if summary:
        system_content += f"\n\nThe student is working on summarizing the following topic: {summary.title}"
    
    # Format the conversation for OpenAI
    formatted_messages = [
        {"role": "system", "content": system_content}
    ]
    
    # Add the conversation history
    for msg in messages:
        role = "user" if msg.sender == "user" else "assistant"
        formatted_messages.append({"role": role, "content": msg.message})
    
    # Get response from OpenAI
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=formatted_messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "I'm having trouble connecting right now. Please try again later."

def generate_summary(content, title):
    """
    Generate a summary of the provided content
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an academic summarization assistant. Create a concise summary of the following content, highlighting the key concepts and their relationships."},
                {"role": "user", "content": f"Title: {title}\n\nContent: {content}\n\nPlease provide a summary in 3-4 paragraphs."}
            ],
            max_tokens=800,
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Unable to generate summary at this time."

def extract_concepts(content, title):
    """
    Extract key concepts from the content using an improved prompt inspired by coworkers
    """
    try:
        # Using the improved prompt from coworkers
        prompt_string = """
        Analyze the provided text with precision and structure.
        ### 1.  Identify Key Concepts:  
        - Extract exactly 10 fundamental key concepts essential to understanding the text.  
        - DO NOT introduce any additional terms beyond those directly discussed in the text.  
        - Ensure that every concept is used in causal relations.  
        
        ### 2. Generate a Structured Summary (Max 600 Words):  
        - Provide a detailed yet concise summary of the document's core ideas.  
        - The summary must naturally include the extracted key concepts and explain their relationships.  
        - Ensure completeness: No cut-off text, and all key principles must be clearly explained.  
        - Avoid unnecessary examples or irrelevant details.  
        
        ### 3. Map Causal Relations (Strictly Using Extracted Key Concepts):  
        - Identify direct cause-and-effect relationships between the extracted key concepts.  
        - DO NOT introduce additional concepts—only use those from the extracted key concepts list.
        - Each key concept should have at least one causal relationship with another key concept.  
        - Format causal relationships strictly as:  
            - "Concept1 -> Concept2" (A causes B)  
            - "Concept1 <-> Concept2" (Bidirectional relationship)  
        - Ensure 10-15 causal relations that accurately reflect the text.  
        - Reject broad or redundant relationships (e.g., "Motion -> Dynamics" or "Motion <-> Kinematics").  
        - Order them so if a key concept has multiple relations, they are listed together even if the concept is a cause or effect and if it is a effect you can switch the causal relations so it begins with the effect and is <- by the cause.
        
        Format your response as JSON with:
        - 'concepts' as a list of concept names (exactly 10)
        - 'summary' as a string containing the structured summary
        - 'relationships' as a list of objects with 'source', 'target', and 'relationship_type' properties
        
        Title: {title}
        Content: {content}
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a concept extraction and relationship mapping assistant."},
                {"role": "user", "content": prompt_string.format(title=title, material=content)}
            ],
            max_tokens=1500,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        # Ensure we have the expected structure
        if "concepts" not in result:
            result["concepts"] = []
        if "relationships" not in result:
            result["relationships"] = []
        if "summary" not in result:
            result["summary"] = ""
            
        # Convert any causal relations format like "A -> B" to standardized objects
        processed_relationships = []
        
        # First handle any relationships that might already be in object format
        if isinstance(result["relationships"], list):
            for rel in result["relationships"]:
                if isinstance(rel, dict) and "source" in rel and "target" in rel:
                    processed_relationships.append(rel)
                elif isinstance(rel, str):
                    # Parse string relationship
                    if "->" in rel:
                        source, target = [s.strip() for s in rel.split("->")]
                        processed_relationships.append({"source": source, "target": target, "relationship_type": "causes"})
                    elif "<-" in rel:
                        target, source = [s.strip() for s in rel.split("<-")]
                        processed_relationships.append({"source": source, "target": target, "relationship_type": "causes"})
                    elif "<->" in rel:
                        source, target = [s.strip() for s in rel.split("<->")]
                        processed_relationships.append({"source": source, "target": target, "relationship_type": "bidirectional"})
        
        result["relationships"] = processed_relationships
        return result
    except Exception as e:
        print(f"Error extracting concepts: {e}")
        return {"concepts": [], "relationships": [], "summary": ""}

def evaluate_summary(original_content, summary_content):
    """
    Evaluate the quality of a summary compared to the original content using an improved analysis approach
    """
    try:
        # First, extract key concepts from the original content
        concept_data = extract_concepts(original_content, "Original Content Analysis")
        key_concepts = concept_data.get("concepts", [])
        
        # Now evaluate the summary against these key concepts
        prompt = f"""
        I want you to carefully evaluate a student's summary against the original content. 
        
        First, analyze which of these key concepts from the original text are present in the summary:
        {', '.join(key_concepts)}
        
        Original content: {original_content}

        Student summary: {summary_content}

        Provide your evaluation as JSON with the following properties:
        1. 'score': A number from 1-5 representing the quality of the summary (5 being excellent)
        2. 'feedback': Specific feedback on the summary's strengths and areas for improvement
        3. 'missing_concepts': A list of key concepts from the original that are missing from the summary
        4. 'present_concepts': A list of key concepts from the original that are present in the summary

        Carefully check for each concept - they might be expressed using different wording but similar meaning.
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a summary evaluation assistant that accurately identifies which key concepts are present and missing in student summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure we have the expected fields
        if "present_concepts" not in result:
            result["present_concepts"] = []
            
        if "missing_concepts" not in result and key_concepts:
            # If missing_concepts isn't provided, derive it from present_concepts
            present_set = set(result.get("present_concepts", []))
            result["missing_concepts"] = [c for c in key_concepts if c not in present_set]
            
        return result
    except Exception as e:
        print(f"Error evaluating summary: {e}")
        return {"score": 0, "feedback": "Error evaluating summary", "missing_concepts": [], "present_concepts": []}
from transformers import pipeline, BertForSequenceClassification,BertTokenizerFast
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv(r"C:\Users\MegaS\OneDrive\Desktop\Python_Stuff\AIM_HIGH\.env")
classification_model_path = r"C:\Users\MegaS\OneDrive\Desktop\Python_Stuff\AIM_HIGH\AIM_HIGH\BERT_Classification_Model"

model = BertForSequenceClassification.from_pretrained(classification_model_path)
tokenizer = BertTokenizerFast.from_pretrained(classification_model_path)
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

client = OpenAI()

appropriate_input = True # Turns false if user inputs inappropriate query
current_query = "" # Is equal to whatever activity is currently going on like a summary assignment in progress

def Classify(user_input):# Runs input through classification model
    prediction = nlp(user_input)
    print(f"Classification: {prediction[0]['label']}")
    return(prediction[0]["label"])

def Hidden_Prompt(user_input, classification):
    # All instructions here are temporary until full system(s) is put in place
    global current_query
    global appropriate_input
    appropriate_input = True
    if classification == "summary_assignment" and current_query != classification:
        current_query = classification
        return f"{user_input} Hidden Instructions: To create a summary assignment, take this data:  “Type 2 diabetes is a chronic condition affecting how the body processes blood sugar. A person with type 2 diabetes has a body that resists or rejects insulin. Risk factors: • Obesity/overweight • Physical inactivity • Age (40+) • Family history • Poor diet Symptoms: • Increased thirst • Frequent urination • Increased hunger • Fatigue • Blurred vision • Frequent infections Potential Complications: • Heart disease • Kidney damage • Eye problems • Skin conditions Ways to prevent: - Changing your lifestyle to exercise more, maintain a healthy diet, and managing stress can help prevent diabetes.” and write a brief summary. Once you’ve done that, tell the user the summary assignment has been created."
    elif classification == "register_content" and current_query != classification:
        current_query = classification
        return f"{user_input} Hidden Instructions: To register content, ask the user what content they’d like to register. Then the content will be automatically registered. After the user says what content they’d like to register tell them the content has been registered."
    elif classification == "causal_relation_analysis" and current_query != classification:
        current_query = classification
        return f"{user_input} Hidden Instructions: To make a relational analysis assignment, take this data: “Type 2 diabetes is a chronic condition affecting how the body processes blood sugar. A person with type 2 diabetes has a body that resists or rejects insulin. Risk factors: • Obesity/overweight • Physical inactivity • Age (40+) • Family history • Poor diet Symptoms: • Increased thirst • Frequent urination • Increased hunger • Fatigue • Blurred vision • Frequent infections Potential Complications: • Heart disease • Kidney damage • Eye problems • Skin conditions Ways to prevent: - Changing your lifestyle to exercise more, maintain a healthy diet, and managing stress can help prevent diabetes.” and find key relations in the summary and output them with dashes between each key relations with commas separating groups of key relations. Once you’ve done that, tell the user the relational analysis assignment has been created."
    elif classification == "none":
        return user_input # can be changed if we do something with the unrelated queries
    elif classification == "inappropriate":
        appropriate_input = False
        return "Inappropriate content detected, please try again"
    else:
        return user_input  # If the input is none of the cases

def chat_loop():
    conversation_history = [
        {"role": "system",
         "content": "You are a 35 year old doctor-bot who helps the user create and save assignments as well as teaches the user about their assignments."}
    ]

    while True:
        try:
            user_input = input("Raw Input: ")

            if user_input.lower() == 'quit':
                break

            classification = Classify(user_input) # classify input as summarization, registration, causal analysis, none, or inappropriate
            llm_input = Hidden_Prompt(user_input, classification) # append new hidden prompt and send it to llm
            if not appropriate_input:
                print(llm_input)
                continue

            conversation_history.append({"role": "user", "content": llm_input})

            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history
            )

            assistant_response = completion.choices[0].message

            print(f"User: {llm_input}")

            print("\nDoctor-bot:", assistant_response.content, "\n")

            conversation_history.append({"role": "assistant", "content": assistant_response.content})

        except Exception as e:
            print(f"An error occurred: {e}")
            continue

chat_loop()

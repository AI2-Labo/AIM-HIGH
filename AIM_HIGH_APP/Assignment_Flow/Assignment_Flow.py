# Main script that references all the others
import Hidden_Prompt_Info, Set_Up_Profiles, Register_Content, Summary_Assignment, Relational_Analysis_Assignment

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import threading

app = FastAPI()

# These should be done externally, this is temp
AI_Profile = Set_Up_Profiles.AI_Profile("Doctor-bot", 40,
                                        "A doctor-bot who helps the user create and save assignments as well as teaches the user about their assignments.",
                                        "PhD in Neuroscience")
My_Profile = Set_Up_Profiles.My_Profile("Joe", 18, "Freshman Economics Student at Econ University")

# Also should be done externally
system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user register content."

# Also should be done externally
initial_hidden_prompt = f"{Hidden_Prompt_Info.register_content_hidden_prompts[0]}"

@app.on_event("startup")
def initialize_flow():
    # Run the flow in a background thread to avoid blocking the server
    flow_thread = threading.Thread(target=run_flow)
    flow_thread.daemon = True  # Allow thread to exit when the server stops
    flow_thread.start()

conversation_history = []

def start_flow(assignment):
    global initial_hidden_prompt
    global system_prompt
    global conversation_history
    if assignment == "Register_Content":
        initial_hidden_prompt = f"{Hidden_Prompt_Info.register_content_hidden_prompts[0]}"
        system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user register content."
        conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_hidden_prompt}
        ]
        register_material = Register_Content.RegisterMaterial(conversation_history, AI_Profile.name, My_Profile.name)
        generator = register_material.start_registration()
    elif assignment == "Summary_Assignment":
        initial_hidden_prompt = f"{Hidden_Prompt_Info.summary_assignment_hidden_prompts[0]}"
        system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user create a summary assignment. If the user wants you to take an action like regenerating, dropping, adding, or registering, tell them you'll complete the action and share it with them shortly. Then, fill out the corresponding JSON parameter associated with the action."
        conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_hidden_prompt}
        ]
        summary_assignment = Summary_Assignment.SummaryAssignment(conversation_history, AI_Profile.name, My_Profile.name)
        generator = summary_assignment.start_summary_assignment()
    elif assignment == "Relational_Analysis":
        system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user create a causal-relations analysis assignment. If the user wants you to take an action like regenerating, dropping, adding, or registering, tell them you'll complete the action and share it with them shortly. Then, fill out the corresponding JSON parameter associated with the action."
        initial_hidden_prompt = f"{Hidden_Prompt_Info.relational_analysis_hidden_prompts[0]}"
        conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_hidden_prompt}
        ]
        relational_analysis_assignment = Relational_Analysis_Assignment.RelationalAssignment(conversation_history, AI_Profile.name, My_Profile.name)
        generator = relational_analysis_assignment.start_relational_assignment()

    for context in generator:
        conversation_history = context
        yield conversation_history
@app.get("/")
async def get():
    return JSONResponse(conversation_history)
def run_flow(): # Edit this function for stuff to happen
    # uvicorn Assignment_Flow:app --reload     <-- Run in terminal once in the Assignment_Flow directory
    global conversation_history
    # Replace "Register_Content" with your desired assignment
    generator = start_flow("Relational_Analysis")
    for context in generator:
        conversation_history = context  # Update the global variable
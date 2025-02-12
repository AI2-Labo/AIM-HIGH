# Main script that references all the others
from openai import OpenAI
import Hidden_Prompt_Info, Set_Up_Profiles, Register_Content, Summary_Assignment, Relational_Analysis_Assignment

client = OpenAI()

# These should be done externally, this is temp
AI_Profile = Set_Up_Profiles.AI_Profile("Doctor-bot", 40,
                                        "A doctor-bot who helps the user create and save assignments as well as teaches the user about their assignments.",
                                        "PhD in Neuroscience")
My_Profile = Set_Up_Profiles.My_Profile("Joe", 18, "Freshman Economics Student at Econ University")

# Also should be done externally
system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user register content."
#system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user register content."
#system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user create a summary assignment. If the user wants you to take an action like regenerating, dropping, adding, or registering, tell them you'll complete the action and share it with them shortly. Then, fill out the corresponding JSON parameter associated with the action."
#system_prompt = f"{AI_Profile.information()} {My_Profile.information()}. You're going to help the user create a causal-relations analysis assignment. If the user wants you to take an action like regenerating, dropping, adding, or registering, tell them you'll complete the action and share it with them shortly. Then, fill out the corresponding JSON parameter associated with the action."

# Also should be done externally
initial_hidden_prompt = f"Hidden Prompt: {Hidden_Prompt_Info.register_content_hidden_prompts[0]}"
#initial_hidden_prompt = f"Hidden Prompt: {Hidden_Prompt_Info.register_content_hidden_prompts[0]}"
#initial_hidden_prompt = f"Hidden Prompt: {Hidden_Prompt_Info.summary_assignment_hidden_prompts[0]}"
#initial_hidden_prompt = f"Hidden Prompt: {Hidden_Prompt_Info.relational_analysis_hidden_prompts[0]}"
conversation_history = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": initial_hidden_prompt}
]
def start_flow(assignment):
    global initial_hidden_prompt
    if assignment == "Register_Content":
        Register_Content.start_registration()
    elif assignment == "Summary_Assignment":
        Summary_Assignment.start_summary_assignment()
    elif assignment == "Relational_Analysis":
        Relational_Analysis_Assignment.start_relational_assignment()

if __name__ == "__main__":
    start_flow("Relational_Analysis")

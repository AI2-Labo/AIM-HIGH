from openai import OpenAI
from pydantic import BaseModel
import json

import Hidden_Prompt_Info, Assignment_Flow, Set_Up_Profiles, Summary_Assignment, Relational_Analysis_Assignment

client = OpenAI()

response_format = Hidden_Prompt_Info.ConfirmationJson
start_feedback_loop = False
def start_summary_assignment():
    global response_format
    global start_feedback_loop
    response_delay = False # For giving a 1 cycle delay
    while True:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=Assignment_Flow.conversation_history,
            response_format=response_format
        )

        assistant_response = completion.choices[0].message
        response_dict = json.loads(assistant_response.content)
        parsed_response = response_dict["message"]

        if response_format == Hidden_Prompt_Info.ConfirmationJson:
            confirmation_response = response_dict["confirmation"]
            if response_delay:
                if confirmation_response == "YES":
                    print(f"Confirmation Response Recorded: {confirmation_response}")
                    response_format = Hidden_Prompt_Info.ReferenceSummaryFeedback
                    start_feedback_loop = True
                else:
                    response_delay = False # Resetting the flip so it tries again
            response_delay = not response_delay  # flips bool to set a 1 cycle delay

        print(f"\n{Assignment_Flow.AI_Profile.name}:", parsed_response)

        Assignment_Flow.conversation_history.append({"role": "assistant", "content": assistant_response.content})
        #print(f"    conversation history: {Assignment_Flow.conversation_history}")

        hidden_instructions = hidden_instructions_func(response_dict)
        if not start_feedback_loop:
            user_input = input(f"{Assignment_Flow.My_Profile.name}: ")
        else:
            user_input = ""
            start_feedback_loop = False

        Assignment_Flow.conversation_history.append({"role": "user", "content": f"{user_input} {hidden_instructions}"})

def hidden_instructions_func(response_dict):
    hidden_instructions = None
    global response_format
    global start_feedback_loop
    if start_feedback_loop:
        return Hidden_Prompt_Info.summary_assignment_hidden_prompts[1]
    if response_format == Hidden_Prompt_Info.ReferenceSummaryFeedback:
        try:
            if response_dict["feedback"] == "YES":
                print("Confirmation Response Recorded: YES")
                start_feedback_loop = True
                return Hidden_Prompt_Info.summary_assignment_hidden_prompts[2]
            elif response_dict["feedback"] == "REGENERATE":
                print("Regeneration Response Recorded")
                start_feedback_loop = True
                return Hidden_Prompt_Info.summary_assignment_hidden_prompts[3]
            elif response_dict["feedback"] == "DROP":
                print(f"Drop Response Recorded: {response_dict['dropped_item']}")
                start_feedback_loop = True
                return Hidden_Prompt_Info.summary_assignment_hidden_prompts[4]
            elif response_dict["feedback"] == "ADD":
                print(f"Add Response Recorded: {response_dict['added_item']}")
                start_feedback_loop = True
                return Hidden_Prompt_Info.summary_assignment_hidden_prompts[5]
            elif response_dict["feedback"] == "NO":
                return hidden_instructions
        except KeyError:
            return hidden_instructions


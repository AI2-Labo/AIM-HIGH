from openai import OpenAI
from pydantic import BaseModel
import json

import Hidden_Prompt_Info, Assignment_Flow, Set_Up_Profiles, Summary_Assignment, Relational_Analysis_Assignment

client = OpenAI()

response_format = Hidden_Prompt_Info.BaseJson
def start_registration():
    global response_format
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
                    response_format = Hidden_Prompt_Info.BaseJson # Resetting
                else:
                    response_delay = False # Resetting the flip so it tries again
            response_delay = not response_delay  # flips bool to set a 1 cycle delay

        print(f"\n{Assignment_Flow.AI_Profile.name}:", parsed_response)

        Assignment_Flow.conversation_history.append({"role": "assistant", "content": assistant_response.content})


        user_input = input(f"{Assignment_Flow.My_Profile.name}: ")

        print(f"User: {user_input}")

        hidden_instructions = parse_hidden_instructions(user_input.lower())

        Assignment_Flow.conversation_history.append({"role": "user", "content": f"{user_input} {hidden_instructions}"})

        #print(f"    conversation history: {Assignment_Flow.conversation_history}")

# Temp function that should be replaced with buttons/non text input
def parse_hidden_instructions(input_string):
    hidden_instructions = None
    global response_format
    if "<<" in input_string:
        if "<<material:" in input_string:
            start_index = input_string.find("<<material:") + len("<<material:")
            end_index = input_string.find(">>", start_index)
            if end_index != -1:
                material_type = input_string[start_index:end_index]
                if material_type in Hidden_Prompt_Info.materials:
                    hidden_instructions = Hidden_Prompt_Info.materials[material_type]

        elif "<<register_material>>" in input_string:
            hidden_instructions = Hidden_Prompt_Info.register_content_hidden_prompts[1]
            response_format = Hidden_Prompt_Info.ConfirmationJson

        elif "<<edit>>" in input_string:
            hidden_instructions = Hidden_Prompt_Info.register_content_hidden_prompts[2]

        elif "<<delete>>" in input_string:
            hidden_instructions = Hidden_Prompt_Info.register_content_hidden_prompts[3]
            response_format = Hidden_Prompt_Info.ConfirmationJson
    return hidden_instructions
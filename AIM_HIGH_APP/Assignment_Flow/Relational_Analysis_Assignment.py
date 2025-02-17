from openai import OpenAI
from pydantic import BaseModel
import json

import Hidden_Prompt_Info, Assignment_Flow, Set_Up_Profiles, Summary_Assignment, Relational_Analysis_Assignment

client = OpenAI()

response_format = Hidden_Prompt_Info.ConfirmationJson
class RelationalAssignment:
    def __init__(self, conversation_history, ai_profile_name, my_profile_name, start_feedback_loop=False, response_format=Hidden_Prompt_Info.ConfirmationJson):
        self.conversation_history = conversation_history
        self.ai_profile_name = ai_profile_name
        self.my_profile_name = my_profile_name
        self.start_feedback_loop = False
        self.response_format = response_format

    def start_relational_assignment(self):
        response_delay = False # For giving a 1 cycle delay
        while True:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=self.conversation_history,
                response_format=self.response_format
            )

            assistant_response = completion.choices[0].message
            response_dict = json.loads(assistant_response.content)
            parsed_response = response_dict["message"]

            if self.response_format == Hidden_Prompt_Info.ConfirmationJson:
                confirmation_response = response_dict["confirmation"]
                if response_delay:
                    if confirmation_response == "YES":
                        print(f"Confirmation Response Recorded: {confirmation_response}")
                        self.response_format = Hidden_Prompt_Info.ReferenceSummaryFeedback
                        self.start_feedback_loop = True
                    else:
                        response_delay = False # Resetting the flip so it tries again
                response_delay = not response_delay  # flips bool to set a 1 cycle delay

            print(f"\n{self.ai_profile_name}:", parsed_response)

            self.conversation_history.append({"role": "assistant", "content": assistant_response.content})
            #print(f"    conversation history: {self.conversation_history}")

            hidden_instructions = self.hidden_instructions_func(response_dict)
            if not self.start_feedback_loop:
                user_input = input(f"{self.my_profile_name}: ")
            else:
                user_input = ""
                self.start_feedback_loop = False

            self.conversation_history.append({"role": "user", "content": f"{user_input} {hidden_instructions}"})

    def hidden_instructions_func(self, response_dict):
        hidden_instructions = ""
        if self.start_feedback_loop:
            return Hidden_Prompt_Info.relational_analysis_hidden_prompts[1]
        if self.response_format == Hidden_Prompt_Info.ReferenceSummaryFeedback:
            try:
                if response_dict["feedback"] == "YES":
                    print("Confirmation Response Recorded: YES")
                    self.start_feedback_loop = True
                    return Hidden_Prompt_Info.relational_analysis_hidden_prompts[2]
                elif response_dict["feedback"] == "REGENERATE":
                    print("Regeneration Response Recorded")
                    self.start_feedback_loop = True
                    return Hidden_Prompt_Info.relational_analysis_hidden_prompts[3]
                elif response_dict["feedback"] == "DROP":
                    print(f"Drop Response Recorded: {response_dict['dropped_item']}")
                    self.start_feedback_loop = True
                    return Hidden_Prompt_Info.relational_analysis_hidden_prompts[4]
                elif response_dict["feedback"] == "ADD":
                    print(f"Add Response Recorded: {response_dict['added_item']}")
                    self.start_feedback_loop = True
                    return Hidden_Prompt_Info.relational_analysis_hidden_prompts[5]
                elif response_dict["feedback"] == "NO":
                    return hidden_instructions
            except KeyError:
                return hidden_instructions


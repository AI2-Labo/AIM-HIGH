from ollama import Client
import json
from AIM_HIGH.aim_high_app.utils import Hidden_Prompt_Info
import os
from dotenv import load_dotenv

load_dotenv()
client = Client(host=os.getenv("OLLAMA_HOST_URL"))

class RegisterMaterial:
    def __init__(self, conversation_history, ai_profile_name, my_profile_name, response_format=Hidden_Prompt_Info.BaseJson):
        self.conversation_history = conversation_history
        self.ai_profile_name = ai_profile_name
        self.my_profile_name = my_profile_name
        self.response_format = response_format

    def start_registration(self):
        response_delay = False # For giving a 1 cycle delay
        while True:
            completion = client.chat(
                model="llama3.3:latest",
                messages=self.conversation_history,
                format=self.response_format.model_json_schema()
            )

            assistant_response = completion['message']['content']
            response_dict = json.loads(assistant_response)
            parsed_response = response_dict["message"]

            if self.response_format == Hidden_Prompt_Info.ConfirmationJson:
                confirmation_response = response_dict["confirmation"]
                if response_delay:
                    if confirmation_response == "YES":
                        print(f"Confirmation Response Recorded: {confirmation_response}")
                        self.response_format = Hidden_Prompt_Info.BaseJson # Resetting
                    else:
                        response_delay = False # Resetting the flip so it tries again
                response_delay = not response_delay  # flips bool to set a 1 cycle delay

            print(f"\n{self.ai_profile_name}:", parsed_response)

            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            yield self.conversation_history # apparently returns updated context

            user_input = input(f"{self.my_profile_name}: ")

            print(f"User: {user_input}")

            hidden_instructions = self.parse_hidden_instructions(user_input.lower())

            self.conversation_history.append({"role": "user", "content": f"{user_input} {hidden_instructions}"})

            yield self.conversation_history # apparently returns updated context

            #print(f"    conversation history: {self.conversation_history}")

    # Temp function that should be replaced with buttons/non text input
    def parse_hidden_instructions(self, input_string):
        hidden_instructions = ""
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
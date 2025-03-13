from ollama import Client
import json
import time
import test_summary2
from AIM_HIGH.aim_high_app.utils import Hidden_Prompt_Info
import os
from dotenv import load_dotenv

load_dotenv()
client = Client(host=os.getenv("OLLAMA_HOST_URL"))

current_summary_assignment = test_summary2.Recieve_Input()

class SummaryAssignment:
    def __init__(self, conversation_history, ai_profile_name, my_profile_name, start_feedback_loop=False, response_format=Hidden_Prompt_Info.ConfirmationJson):
        self.conversation_history = conversation_history
        self.ai_profile_name = ai_profile_name
        self.my_profile_name = my_profile_name
        self.start_feedback_loop = False
        self.response_format = response_format
    def start_summary_assignment(self):
        response_delay = False # For giving a 1 cycle delay
        while True:
            #print("CONTEXT: ", self.conversation_history)
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
                        self.response_format = Hidden_Prompt_Info.ReferenceSummaryFeedback
                        self.start_feedback_loop = True
                    else:
                        response_delay = False # Resetting the flip so it tries again
                response_delay = not response_delay  # flips bool to set a 1 cycle delay

            print(f"\n{self.ai_profile_name}:", parsed_response)

            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            #print(f"    self.conversation history: {self.conversation_history}")

            hidden_instructions = self.hidden_instructions_func(response_dict)
            if not self.start_feedback_loop:
                user_input = input(f"{self.my_profile_name}: ")
            else:
                user_input = ""
                self.start_feedback_loop = False

            self.conversation_history.append({"role": "user", "content": f"{user_input} {hidden_instructions}"})

    def hidden_instructions_func(self, response_dict):
        hidden_instructions = ""

        def wait_for_execution(operation_func):
            # Block until operation is complete
            operation_ready = False
            operation_result = None

            def execute_operation():
                nonlocal operation_ready, operation_result
                operation_result = operation_func()
                operation_ready = True

            execute_operation()

            # Wait until operation is ready
            while not operation_ready:
                time.sleep(0.1)

            return operation_result

        if self.start_feedback_loop:
            def generate_summary_operation():
                return current_summary_assignment.generate(
                    "Uniform Circular Motion",
                    r"C:\Users\MegaS\Downloads\6.2 Dynamics of Uniform Circular Motion.pdf"
                )

            generated_summary = wait_for_execution(generate_summary_operation)
            self.conversation_history.append({"role": "user", "content": ""})
            self.conversation_history.append({"role": "assistant", "content": generated_summary})
            print("\n", generated_summary)
            self.response_format = Hidden_Prompt_Info.ReferenceSummaryFeedback
            return Hidden_Prompt_Info.summary_assignment_hidden_prompts[1]

        if self.response_format == Hidden_Prompt_Info.ReferenceSummaryFeedback:
            try:
                if response_dict["feedback"] == "YES":
                    def save_operation():
                        return current_summary_assignment.save_assignment()

                    saved_assignment = wait_for_execution(save_operation)
                    self.conversation_history.append({"role": "user", "content": ""})
                    self.conversation_history.append({"role": "assistant", "content": saved_assignment})
                    self.start_feedback_loop = True
                    print("\n", saved_assignment)
                    return Hidden_Prompt_Info.summary_assignment_hidden_prompts[2]

                elif response_dict["feedback"] == "REGENERATE":
                    def regenerate_operation():
                        return current_summary_assignment.regenerate()

                    regenerated_summary = wait_for_execution(regenerate_operation)
                    self.conversation_history.append({"role": "user", "content": ""})
                    self.conversation_history.append({"role": "assistant", "content": regenerated_summary})
                    print("\n", regenerated_summary)
                    self.start_feedback_loop = True
                    return Hidden_Prompt_Info.summary_assignment_hidden_prompts[3]

                elif response_dict["feedback"] == "DROP":
                    def drop_operation():
                        return current_summary_assignment.drop_concept(response_dict['dropped_item'])

                    dropped_summary = wait_for_execution(drop_operation)
                    self.conversation_history.append({"role": "user", "content": ""})
                    self.conversation_history.append({"role": "assistant", "content": dropped_summary})
                    print("\n", dropped_summary)
                    self.start_feedback_loop = True
                    return Hidden_Prompt_Info.summary_assignment_hidden_prompts[4]

                elif response_dict["feedback"] == "ADD":
                    def add_operation():
                        return current_summary_assignment.add_concept(response_dict['added_item'])

                    added_summary = wait_for_execution(add_operation)
                    self.conversation_history.append({"role": "user", "content": ""})
                    self.conversation_history.append({"role": "assistant", "content": added_summary})
                    print("\n", added_summary)
                    self.start_feedback_loop = True
                    return Hidden_Prompt_Info.summary_assignment_hidden_prompts[5]

                elif response_dict["feedback"] == "NO":
                    return hidden_instructions

            except KeyError:
                return hidden_instructions

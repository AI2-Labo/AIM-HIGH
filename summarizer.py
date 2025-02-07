from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import sys
import re


# Initialize OpenAI model
llm = ChatOpenAI(
    model_name="gpt-4",  # You can change this to "gpt-3.5-turbo" to save costs
    temperature=0.5  # Controls randomness (0 = focused, 1 = more creative)
)


# Define summarization prompt
prompt_with_modifications = PromptTemplate(
    input_variables=["text", "modification"],
    template="Summarize the following text in a clear and concise way. {modification}\n\n{text}"
)


def split_text(text, max_length=2000):
    """Splits text into chunks while preserving paragraphs."""
    paragraphs = text.split("\n\n")  # Split text into paragraphs


    chunks = []
    current_chunk = ""


    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 > max_length:  # +2 for the newlines
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph  # Start new chunk
        else:
            current_chunk += paragraph + "\n\n"


    if current_chunk:
        chunks.append(current_chunk.strip())


    return chunks


def clean_text(text):
    """Cleans text while preserving paragraph breaks, removing extra blank lines."""
    cleaned_text = re.sub(r'\n\s*\n+', '\n\n', text.strip())
    return cleaned_text


def summarize_text(text, modification=""):
    """Summarizes the input text, processing chunks if needed."""
    MAX_LENGTH = 2000  # Safe limit for OpenAI API
    text_chunks = split_text(text, MAX_LENGTH)  


    if not text_chunks:
        return "⚠️ Error: No valid text chunks to summarize."


    chunk_summaries = []
    for i, chunk in enumerate(text_chunks):
        print(f"\n🔹 Summarizing chunk {i+1}/{len(text_chunks)}...\n")
        formatted_prompt = prompt_with_modifications.format(text=chunk, modification=modification)
        try:
            summary = llm.invoke(formatted_prompt).content
            chunk_summaries.append(summary)  
        except Exception as e:
            print(f"⚠️ Error summarizing chunk {i+1}: {e}")
            continue


    # Combine all chunk summaries into one text
    combined_summary = "\n\n".join(chunk_summaries)


    print("\n🔹 Generating Final Summary...\n")
    final_prompt = prompt_with_modifications.format(text=combined_summary, modification=modification)
    try:
        final_summary = llm.invoke(final_prompt).content  
    except Exception as e:
        print(f"⚠️ Error generating final summary: {e}")
        return "Error: Unable to generate final summary."


    return final_summary.strip()


def regenerate_summary(summary, modification):
    """Regenerates summary based on user-specified modifications."""
    formatted_prompt = prompt_with_modifications.format(text=summary, modification=modification)
    new_summary = llm.invoke(formatted_prompt).content
    return new_summary.strip()


if __name__ == "__main__":
    print("Enter the text you want to summarize (press Enter twice when done):")


    # Capture multi-line input
    user_text = []
    blank_line_count = 0  


    while True:
        try:
            line = input()
            if line.strip() == "":
                blank_line_count += 1
                if blank_line_count == 2:
                    break
                user_text.append("")  
            else:
                blank_line_count = 0  
                user_text.append(line)
        except EOFError:
            break


    user_text = "\n".join(user_text)  
    cleaned_text = clean_text(user_text)  


    # Split into paragraphs for selection
    paragraphs = cleaned_text.split("\n\n")
   
    # Display numbered paragraphs
    print("\n🔹 The text has been divided into the following sections:\n")
    for i, paragraph in enumerate(paragraphs, 1):
        print(f"[{i}] {paragraph[:200]}...")  


    # Allow user to select paragraphs
    selected_indexes = input("\nEnter the paragraph numbers to summarize (comma-separated, e.g., 1,3,5): ").strip()
    selected_indexes = [int(i) - 1 for i in selected_indexes.split(",") if i.isdigit()]


    # Extract selected sections
    selected_text = "\n\n".join([paragraphs[i] for i in selected_indexes if 0 <= i < len(paragraphs)])


    if not selected_text.strip():
        print("⚠️ Error: No valid sections selected!")
    else:
        summary = summarize_text(selected_text)  
        print("\n🔹 Initial Summary:\n", summary)


        # ✅ Only allow modifications if a valid summary was generated
        modify_choice = input("\nWould you like to modify the summary? (yes/no): ").strip().lower()


        if modify_choice == "yes":
            while True:
                action = input("\nType 'add' to add a key concept, 'remove' to delete one, or 'done' to finish: ").strip().lower()
               
                if action == "add":
                    new_concept = input("Enter the key concept to ADD: ").strip()
                    modification_instruction = f"Ensure that the concept '{new_concept}' is included in the summary."
                    summary = regenerate_summary(summary, modification_instruction)  # Regenerate summary
                    print("\n🔹 Updated Summary:\n", summary)


                elif action == "remove":
                    remove_concept = input("Enter the key concept to REMOVE: ").strip()
                    modification_instruction = f"Remove any mention of '{remove_concept}' from the summary."
                    summary = regenerate_summary(summary, modification_instruction)  # Regenerate summary
                    print("\n🔹 Updated Summary:\n", summary)


                elif action == "done":
                    break


                else:
                    print("⚠️ Invalid option. Please type 'add', 'remove', or 'done'.")


        print("\n🔹 Final Summary:\n", summary)




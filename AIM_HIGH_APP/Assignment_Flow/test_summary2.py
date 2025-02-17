import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader


class Recieve_Input:
    def __init__(self, model_name='gpt-3.5-turbo-0125', temperature=0.3):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.topic = ""
        self.material = ""
        self.key_concepts = ""
        self.summary = ""
        self.key_relations = ""

    def load_pdf(self, pdf_path):
        """Loads text content from a PDF file."""
        if not os.path.exists(pdf_path):
            print("❌ File not found.")
            return ""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        if not documents:
            print("⚠️ PDF loaded, but contains no text.")
            return ""

        text = " ".join([page.page_content for page in documents])
        print(f"✅ Loaded {len(text)} characters from the PDF.")
        return text

    def generate(self, topic, pdf_path):
        """Generates the initial reference summary/analysis assignment."""
        self.topic = topic
        if self.material == "": # So it doesn't try to load the already loaded pdf as a path
            self.material = self.load_pdf(pdf_path)
        if not self.material:
            print("❌ Failed to load reading material.")
            return
        
        #print("🔄 Generating summary...")

        prompt_string = """
        You are an expert in physics and technical writing. Your task is to generate a **well-structured, concise, and logically coherent** summary of the topic **"{topic}"** based on the provided reading material: 
        
        1. **Identify And extarct Key Concepts:**
           - Identify essential terms and key concepts related to **"{topic}"**.
           - Extract the key concepts from this document and list them in bullet points.
           - Begin with a count of the total key concepts in parentheses. 
           - list concepts without explanation. 
        
        2. **Generate a Clear and Concise Summary:**
           - Write a **well-structured** summary that smoothly transitions between key ideas.
           - Use **formal yet reader-friendly language** for clarity.
           - Avoid excessive repetition or redundant phrasing. 
           - Ensure each sentence **adds new value** to the explanation.
           - Where appropriate, include **real-world applications** 
           - Use **one or two strong examples** rather than listing many.
           - Ensure a **progressive development of ideas**
           - Make it 600 word long
        
        3. **Define Key Concept Relations:**
           - Identify pairwise relationships between the key concepts.
           - Use the format: `concept1 - concept2`
           - List them **separately** from the summary.
           - Ensure that related terms are grouped together logically.
           - the key relations should give a clear understanding of all the relevenent relationships made in the learnding material.
        
        ### Reading Material:
        {material}
        """
        
        prompt = PromptTemplate.from_template(prompt_string)
        chain = LLMChain(prompt=prompt, llm=self.llm)
        response = chain.run(topic=self.topic, material=self.material)
        
        self.summary = response.strip()

        if self.summary:
            #print("✅ Generated Summary:")
            #print(self.summary)
            return self.summary
        else:
            print("⚠️ No output received from the AI model.")

    def regenerate(self):
        """Regenerates the reference summary/analysis assignment."""
        if not self.material:
            print("❌ No material available. Please generate first.")
            return
        return self.generate(self.topic, self.material)

    def drop_concept(self, concept):
        """Drops a concept from the reference summary and regenerates it."""
        self.key_concepts = self.key_concepts.replace(concept, "").strip()
        return self.modify_summary()
    
    def add_concept(self, concept):
        """Adds a concept to the reference summary and regenerates it."""
        self.key_concepts += f" {concept}" if concept not in self.key_concepts else ""
        return self.modify_summary()

    def modify_summary(self):
        """Regenerates summary with modified key concepts."""
        prompt_string = """
        You will generate a refined summary based on the provided reading material and the current summary. The summary should be:

        1. **Concise:** No more than 600 words.  
        2. **Coherent and Clear:** Ensure clarity and logical flow while embedding the provided key concepts.  
        3. **Key Concept Integration:** The given key concepts must be included naturally within the summary.  
        4. **Example Use:** Avoid detailed real-life examples but briefly reference them to reinforce key concepts where necessary.
        5. **Define Key Concept Relations:**  
        - Identify pairwise relationships between the key concepts mentioned in the summary.  
        - Use the format 'Key Concept1 - Key Concept2' for each significant conceptual relationship.  
        - Separate pairs using '-'.  
        - Focus on significant relationships only and avoid redundant connections.



        
        ### Reading Material:
        {material}
        
        ### Current Summary:
        {summary}
        """
        prompt = PromptTemplate.from_template(prompt_string)
        chain = LLMChain(prompt=prompt, llm=self.llm)
        response = chain.run(material=self.material, key_concepts=self.key_concepts, summary=self.summary)
        
        self.summary = response.strip()

        if self.summary:
            #print("✅ Modified Summary:")
            #print(self.summary)
            return self.summary
        else:
            print("⚠️ No output received from the AI model.")

    def save_assignment(self):
        """Saves the current summary and key concepts."""
        with open("saved_summary.txt", "w") as file:
            file.write(f"Topic: {self.topic}\n")
            file.write(f"Key Concepts: {self.key_concepts}\n")
            file.write(f"Summary: {self.summary}\n")
        return "💾 Assignment saved."


# ✅ **Main Execution Block**
if __name__ == "__main__":
    ai_tool = Recieve_Input()

    # Change the path to your actual PDF file
    pdf_path = r"C:\Users\MegaS\Downloads\6.2 Dynamics of Uniform Circular Motion.pdf"
    topic = "Uniform Circular Motion"

    # 🔄 Generate Initial Summary
    ai_tool.generate(topic, pdf_path)

    # Modify the summary 
    ai_tool.add_concept("Centripetal Force")
    ai_tool.drop_concept("Tangential Acceleration")

    # 💾 Save the summary
    ai_tool.save_assignment()

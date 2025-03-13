import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # Updated import
from langchain_community.document_loaders import PyPDFLoader
from pyvis.network import Network
import networkx as nx

class Recieve_Input:
    def __init__(self, model_name='gpt-3.5-turbo-0125', temperature=0):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.topic = ""
        self.material = ""
        self.key_concepts = ""
        self.summary = ""
        self.causal_relations = ""

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
        """Generates the initial reference summary and causal relations."""
        self.topic = topic
        if self.material == "": # So it doesn't try to load the already loaded pdf as a path
            self.material = self.load_pdf(pdf_path)
        if not self.material:
            print("❌ Failed to load reading material.")
            return
        
        print("🔄 Generating summary and extracting concepts...")

        prompt_string = """
        You will generate a refined Causality Description based on the provided reading material and the current summary. The summary should be:

        1. **Concise:** No more than 600 words.  
        2. **Coherent and Clear:** Ensure clarity and logical flow while embedding the provided key concepts.  
        3. **Key Concept Integration:** The given key concepts must be included naturally within the summary.  
        4. **Example Use:** Avoid detailed real-life examples but briefly reference them to reinforce key concepts where necessary.
        5. **Define Causal Relations among Key Concepts:**  
        - Identify significant pairwise causal relationships among the key concepts mentioned in the description.  
        - Use the format **'Key Concept1 -> Key Concept2'** where the first concept is the cause and the second the result.  
        - Separate pairs using the **@** symbol.  
        - Report only significant causal relations and avoid redundant or implied connections.
        6. Formatted in with these exact sections :
        Summary:
        [your summary here]
        
        Key Concepts:
        [key concepts here]
        
        Causal Relationships:
        [causal relationships here]
          
        Here's the information you should use: 
        ### Topic:
        {topic}
        
        ### Reading Material:
        {material}

        ### Key Concepts:
        key_concepts

        ### Current Summary:
        current_ Causality Description

        Please generate a refined summary that meets the above requirements.
        """
        
        prompt = PromptTemplate.from_template(prompt_string)
        chain = LLMChain(prompt=prompt, llm=self.llm)
        response = chain.run(topic=self.topic, material=self.material)
        
        self.summary, self.key_concepts, self.causal_relations = self.process_response(response)

        if self.summary:
            #print("✅ Generated Summary:")
            #print(self.summary)
            return f"Generated Summary: {self.summary}, Generated Key Concepts: {self.key_concepts}, Extracted Causal Relations: {self.causal_relations}"

        #print("✅ Extracted Key Concepts:")
        #print(self.key_concepts)

        #print("✅ Extracted Causal Relations:")
        #print(self.causal_relations)
        
    def regenerate(self):
        """Regenerates the summary and causal relations."""
        #print("🔄 Regenerating summary and causal relations...")
        if not self.material:
            print("❌ No material available. Please generate first.")
            return
        return self.generate(self.topic, self.material)
    def drop_concept(self, concept):
        """Drops a concept(s) from the reference summary/analysis assignment."""
        #print(f"❌ Dropping concept: {concept}")
        self.key_concepts = self.key_concepts.replace(concept, "")
        return self.key_concepts

    def add_concept(self, concept):
        """Adds a concept(s) to the reference summary/analysis assignment."""
        #print(f"✅ Adding concept: {concept}")
        self.key_concepts += "\n" + concept
        return self.key_concepts

    def save_assignment(self):
        """Saves the reference summary/analysis assignment."""
        with open("saved_summary.txt", "w") as file:
            file.write(f"Topic: {self.topic}\n")
            file.write(f"Summary: {self.summary}\n")
            file.write(f"Key Concepts:\n{self.key_concepts}\n")
            file.write(f"Causal Relationships:\n{self.causal_relations}\n")
        return "💾 Summary and relations saved."

    def process_response(self, response):
        """Process the AI-generated response into summary, key concepts, and causal relations.""" 
        summary = ""
        key_concepts = ""
        causal_relations = ""
        
        sections = response.split("\n\n")
        
        for section in sections:
            if "Summary" in section:
                summary = section.strip()
            elif "Key Concepts" in section:
                key_concepts = section.strip()
            elif "Causal Relationships" in section:
                causal_relations = section.strip()
        
        return summary, key_concepts, causal_relations

    def visualize_graph(self):
        """Visualizes key concepts and causal relations as a directed graph."""
        G = nx.DiGraph()

        # Add key concepts as nodes
        concepts = self.key_concepts.split("\n")
        for concept in concepts:
            if concept.strip():
                G.add_node(concept.strip())

        # Add causal relations as directed edges
        relations = self.causal_relations.split("\n")
        for relation in relations:
            if "->" in relation:
                cause, effect = relation.split("->")
                G.add_edge(cause.strip(), effect.strip())

        # Use Pyvis to visualize the graph
        net = Network(notebook=True, cdn_resources='remote')
        net.from_nx(G)
        net.show("causal_relations_graph.html")
        print("✅ Graph saved as causal_relations_graph.html")


# ✅ **Main Execution Block**
if __name__ == "__main__":
    ai_tool = Recieve_Input()

    # Change the path to your actual PDF file
    pdf_path = r"C:\Users\MegaS\Downloads\6.2 Dynamics of Uniform Circular Motion.pdf"
    topic = "Motion and Forces"

    # 🔄 Generate Summary, Key Concepts, and Causal Relations
    ai_tool.generate(topic, pdf_path)

    # 💻 Visualize the Causal Relations Graph
    ai_tool.visualize_graph()

    # 💾 Save the summary, key concepts, and causal relations
    ai_tool.save_assignment()
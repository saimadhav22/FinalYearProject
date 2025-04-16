from prompt_templates import memory_prompt_template
from langchain.chains import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.vectorstores import Chroma
import chromadb
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def load_normal_chain(chat_history):
    """Loads the normal chat chain."""
    return chatChain(chat_history)


def load_pdf_chat_chain(chat_history):
    """Loads the PDF-based chat chain."""
    return pdfChatChain(chat_history)



def create_llm(model_path=config["model_path"]["large"], model_type=config["model_type"], model_config=config["model_config"]):
    model_config["gpu_layers"] = 0  # ✅ Force CPU mode

    try:
        print(f"⏳ Loading LLM model from: {model_path} on {model_type}")
        llm = CTransformers(model=model_path, model_type=model_type, config=model_config)
        print("✅ LLM Loaded Successfully!")
        return llm
    except Exception as e:
        print("❌ LLM Loading Error:", str(e))
        return None  # ✅ Prevents crash, helps debugging





def create_embeddings(embeddings_path=config["embeddings_path"]):
    """Load embeddings model."""
    return HuggingFaceEmbeddings(model_name=embeddings_path)

def create_chat_memory(chat_history):
    """Initialize conversation memory."""
    return ConversationBufferWindowMemory(memory_key="history", chat_memory=chat_history, k=3)

def create_prompt_from_template(template):
    """Generate a prompt from a template."""
    return PromptTemplate.from_template(template)

def create_llm_chain(llm, chat_prompt, memory):
    """Create a standard LLMChain."""
    return LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

def load_vectordb(embeddings):
    """Load ChromaDB for document storage & metadata tracking."""
    persistent_client = chromadb.PersistentClient("chroma_db")

    # Main vector database for documents
    vector_db = Chroma(
        client=persistent_client,
        collection_name="pdfs",
        embedding_function=embeddings
    )

    # Metadata store for tracking processed PDFs
    hash_store = Chroma(
        client=persistent_client,
        collection_name="pdf_hashes",
        embedding_function=embeddings
    )

    return vector_db, hash_store


def load_retrieval_chain(llm, memory, vector_db):
    retriever = vector_db.as_retriever(search_kwargs={"k": 1})  # ✅ Reduce retrieval complexity
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", memory=memory, retriever=retriever)


class pdfChatChain:
    """Handles PDF-based AI chat."""

    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        self.vector_db, self.hash_store = load_vectordb(create_embeddings())
        llm = create_llm()
        self.llm_chain = load_retrieval_chain(llm, self.memory, self.vector_db)

    def run(self, user_input):
        """Process user queries using vector retrieval."""
        print("📄 Pdf chat chain is running...")

        try:
            print("🔄 Sending query to LLM...")
            response = self.llm_chain.run(query=user_input, history=self.memory.chat_memory.messages, stop=["Human:"])
            print("✅ Response received from LLM!")
        except Exception as e:
            print("❌ Error in LLM processing:", str(e))
            response = "⚠️ An error occurred while processing your request."

        if not response or response.strip() == "":
            response = "⚠️ No relevant information found. Try asking differently!"
            print("⚠️ No response from AI, sending fallback message.")

        print("🤖 AI Response:", response)
        return response  # ✅ Now inside the function




def debug_retrieve(query):
    """Manually test ChromaDB retrieval."""
    vector_db, _ = load_vectordb(create_embeddings())
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    results = retriever.get_relevant_documents(query)
    print("🔍 Retrieved Docs:", results)
    return results

class chatChain:
    """Handles normal chat (non-PDF)."""

    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        llm = create_llm()
        chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = create_llm_chain(llm, chat_prompt, self.memory)

    def run(self, user_input):
        return self.llm_chain.run(human_input=user_input, history=self.memory.chat_memory.messages, stop=["Human:"])

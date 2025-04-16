import hashlib
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from llm_handler import load_vectordb, create_embeddings

import pypdfium2

def get_pdf_hash(pdf_bytes):
    """Generate a unique hash for a PDF file."""
    return hashlib.md5(pdf_bytes).hexdigest()

def extract_text_from_pdf(pdf_bytes):
    """Extract text from a single PDF."""
    pdf_file = pypdfium2.PdfDocument(io.BytesIO(pdf_bytes))
    return "\n".join(pdf_file.get_page(page_number).get_textpage().get_text_range() for page_number in range(len(pdf_file)))
    
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)  # ✅ Reduce chunk size
    return splitter.split_text(text)


def get_document_chunks(text_list):
    """Convert text chunks into LangChain Document objects."""
    documents = []
    for text in text_list:
        for chunk in get_text_chunks(text):
            documents.append(Document(page_content=chunk))
    return documents

def add_documents_to_db(pdfs_bytes):
    """Process and store new PDFs only."""
    vector_db, hash_store = load_vectordb(create_embeddings())

    # ✅ Extract stored hashes correctly
    existing_hashes = set()
    hash_results = hash_store.get(where={})
    if "metadatas" in hash_results and hash_results["metadatas"]:
        existing_hashes = {metadata["hash"] for metadata in hash_results["metadatas"] if "hash" in metadata}

    for pdf in pdfs_bytes:
        pdf_hash = get_pdf_hash(pdf.getvalue())

        if pdf_hash in existing_hashes:
            print("✅ PDF already exists in DB, skipping...")
            continue  # Skip reprocessing

        # Extract text from PDF
        text = extract_text_from_pdf(pdf.getvalue())
        documents = get_document_chunks([text])

        # Store document embeddings
        vector_db.add_documents(documents)

        # Store hash in metadata
        hash_store.add_documents([Document(page_content="", metadata={"hash": pdf_hash})])

        print("✅ New PDF added to DB.")

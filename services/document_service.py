import os
from PyPDF2 import PdfReader
import docx
from .embedding_service import get_embedding, cosine_similarity

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    ext = filepath.split(".")[-1].lower()
    text = ""
    try:
        if ext == "pdf":
            reader = PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif ext == "txt":
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == "docx":
            doc = docx.Document(filepath)
            text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
    return text.strip()


def load_all_docs_text(upload_folder):
    docs_data = {}
    for filename in os.listdir(upload_folder):
        if allowed_file(filename):
            text = extract_text_from_file(os.path.join(upload_folder, filename))
            if text:
                docs_data[filename] = text
    return docs_data


def find_relevant_docs(user_message, docs_dict, threshold=0.78):
    """Find documents whose embeddings are semantically similar to the query."""
    relevant_docs = []
    context = ""

    user_emb = get_embedding(user_message)
    if user_emb is None:
        return [], ""

    for name, content in docs_dict.items():
        print(f"🔎 Processing {name} ...")
        doc_emb = get_embedding(content[:4000])
        sim = cosine_similarity(user_emb, doc_emb)
        print(f"📄 {name} → similarity={sim:.3f}")
        if sim >= threshold:
            relevant_docs.append(name)
            context += f"\n\n### {name}\n{content[:4000]}"
        else:
            print(f"❌ Ignored: {name}")
    return relevant_docs, context


def generate_references_html(relevant_docs):
    """Return clickable HTML references."""
    if not relevant_docs:
        return ""
    refs = "".join(
        [f'<li><a href="/uploads/{name}" target="_blank">{name}</a></li>' for name in relevant_docs]
    )
    return f"<h5>📚 References</h5><ul>{refs}</ul>"

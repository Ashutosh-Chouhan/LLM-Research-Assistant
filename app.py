"""
LLM Research Assistant -- Streamlit UI.

Chalane ke liye:
    streamlit run app.py
"""

import streamlit as st

from src.config import DATA_DIR, TOP_K
from src.loader import load_pdf, load_pdfs_from_dir
from src.rag import answer_question, summarize_documents
from src.splitter import split_documents
from src.vectorstore import build_vectorstore, index_exists, load_vectorstore

st.set_page_config(page_title="LLM Research Assistant", page_icon="📄", layout="wide")


@st.cache_resource(show_spinner=False)
def get_vectorstore():
    """Index ek hi baar load ho, har rerun par nahi -> isliye cache_resource."""
    return load_vectorstore()


def ingest_uploaded_file(uploaded_file, status_area) -> int:
    """Upload ki gayi PDF ko data/ me save karke index banao. Chunk count return."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = DATA_DIR / uploaded_file.name
    saved_path.write_bytes(uploaded_file.getbuffer())

    documents = load_pdf(saved_path)
    chunks = split_documents(documents)

    # Free tier rate limit ki wajah se embedding batches me hoti hai ->
    # user ko progress dikhana zaroori hai, warna app hang laga lagega.
    progress_bar = status_area.progress(0.0, text="Embeddings ban rahi hain...")

    def on_progress(done: int, total: int) -> None:
        progress_bar.progress(done / total, text=f"Embedded {done}/{total} chunks")

    build_vectorstore(chunks, reset=True, on_progress=on_progress)
    progress_bar.empty()

    # Purana cached index hata do, warna naya load nahi hoga
    get_vectorstore.clear()

    st.session_state.documents = documents
    st.session_state.messages = []
    return len(chunks)


# ---------------- Session state ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents" not in st.session_state:
    st.session_state.documents = None


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📄 Document")

    uploaded_file = st.file_uploader("PDF upload karo", type="pdf")

    if uploaded_file is not None:
        if st.button("Process PDF", type="primary", use_container_width=True):
            status_area = st.empty()
            st.caption("Free tier rate limit ki wajah se thoda time lagta hai.")
            try:
                n_chunks = ingest_uploaded_file(uploaded_file, status_area)
                st.success(f"Ho gaya — {n_chunks} chunks indexed.")
            except Exception as exc:
                st.error(f"Ingestion fail hui: {exc}")

    st.divider()
    st.header("⚙️ Settings")
    top_k = st.slider(
        "Kitne chunks retrieve karein (k)",
        min_value=1,
        max_value=10,
        value=TOP_K,
        help="Zyada k = zyada context, lekin dhima aur mehnga.",
    )

    st.divider()
    if index_exists():
        st.caption("✅ Index ready hai.")
    else:
        st.caption("⚠️ Koi index nahi. PDF upload karo ya `python ingest.py` chalao.")

    if st.button("Chat clear karo", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ---------------- Main ----------------
st.title("LLM Research Assistant")
st.caption("Apne research paper se sawaal poocho — jawab sirf usi document se aayega.")

if not index_exists():
    st.info("Shuru karne ke liye sidebar se ek PDF upload karke **Process PDF** dabao.")
    st.stop()

try:
    vectorstore = get_vectorstore()
except Exception as exc:
    st.error(f"Index load nahi hua: {exc}")
    st.stop()

# Summary button
if st.button("📝 Paper ka summary banao"):
    with st.spinner("Summary likh raha hoon..."):
        try:
            # Upload se aaye documents use karo, warna data/ folder se load karo
            documents = st.session_state.documents or load_pdfs_from_dir(DATA_DIR)
            summary = summarize_documents(documents)
        except Exception as exc:
            st.error(f"Summary nahi ban payi: {exc}")
            st.stop()
    st.session_state.messages.append(
        {"role": "assistant", "content": summary, "sources": []}
    )

# Purani chat dikhao
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📚 Sources ({len(message['sources'])} chunks)"):
                for doc in message["sources"]:
                    page = doc.metadata.get("page", 0) + 1
                    file_name = doc.metadata.get("file_name", "unknown")
                    st.markdown(f"**{file_name} — page {page}**")
                    st.text(doc.page_content[:600] + "…")
                    st.divider()

# Naya sawaal
if question := st.chat_input("Apna sawaal likho..."):
    st.session_state.messages.append(
        {"role": "user", "content": question, "sources": []}
    )
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Document search kar raha hoon..."):
            try:
                result = answer_question(vectorstore, question, k=top_k)
            except Exception as exc:
                st.error(f"Error: {exc}")
                st.stop()

        st.markdown(result["answer"])

        if result["sources"]:
            with st.expander(f"📚 Sources ({len(result['sources'])} chunks)"):
                for doc in result["sources"]:
                    page = doc.metadata.get("page", 0) + 1
                    file_name = doc.metadata.get("file_name", "unknown")
                    st.markdown(f"**{file_name} — page {page}**")
                    st.text(doc.page_content[:600] + "…")
                    st.divider()

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )

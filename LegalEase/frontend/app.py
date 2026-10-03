import html
import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.7rem;
        font-weight: 750;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        text-align: center;
        color: #8b95a7;
        margin-bottom: 1.5rem;
    }
    .preview {
        background: #10151d;
        border: 1px solid #273244;
        border-radius: 14px;
        padding: 24px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.7;
    }
    .warning {
        padding: 12px 16px;
        border-radius: 10px;
        background: #2b2415;
        border: 1px solid #735d20;
        color: #f5e5a6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">⚖️ LegalEase</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Generator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="warning">AI-generated draft only. Review the document and '
    'obtain professional legal advice where appropriate.</div>',
    unsafe_allow_html=True,
)
st.write("")

if "document" not in st.session_state:
    st.session_state.document = ""
if "edited" not in st.session_state:
    st.session_state.edited = False

left, right = st.columns([0.9, 1.1], gap="large")

with left:
    st.subheader("Document Details")

    document_type = st.text_input(
        "Document Type",
        placeholder="e.g. Freelance Work Contract",
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), TechNova Inc. (Client)"
        ),
        height=110,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=170,
        help="Separate clauses with semicolons.",
    )

    effective_date = st.text_input(
        "Effective Date",
        value=date.today().strftime("%B %d, %Y"),
    )

    language = st.selectbox(
        "Output Language",
        ["English", "Tamil", "Hindi", "Malayalam", "Telugu", "Kannada"],
    )

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )

    if generate:
        if not all(
            value.strip()
            for value in [document_type, parties, terms, effective_date]
        ):
            st.error("Please fill in Document Type, Parties, Terms, and Effective Date.")
        else:
            payload = {
                "document_type": document_type,
                "parties": parties,
                "terms": terms,
                "effective_date": effective_date,
                "language": language,
            }

            with st.spinner("Generating your document with Gemini..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=120,
                    )
                    if response.ok:
                        data = response.json()
                        st.session_state.document = data["content"]
                        st.session_state.edited = False
                        st.success("Document generated successfully.")
                    else:
                        try:
                            detail = response.json().get("detail", response.text)
                        except Exception:
                            detail = response.text
                        st.error(f"Backend error: {detail}")
                except requests.RequestException as exc:
                    st.error(
                        "Could not connect to FastAPI. Make sure the backend is "
                        f"running at {BACKEND_URL}. Details: {exc}"
                    )

with right:
    st.subheader("Document Preview")

    if st.session_state.document:
        if st.button(
            "✏️ Edit Document",
            use_container_width=True,
        ):
            st.session_state.edited = True

        if st.session_state.edited:
            edited_content = st.text_area(
                "Edit the generated document",
                value=st.session_state.document,
                height=560,
            )
            st.session_state.document = edited_content
        else:
            preview = html.escape(st.session_state.document)
            preview = preview.replace("\n\n", "</p><p>").replace("\n", "<br>")
            st.markdown(
                f'<div class="preview"><p>{preview}</p></div>',
                unsafe_allow_html=True,
            )

        st.write("")
        st.subheader("Download")

        download_cols = st.columns(3)
        for column, file_format, label in zip(
            download_cols,
            ["txt", "docx", "pdf"],
            ["TXT", "DOCX", "PDF"],
        ):
            with column:
                if st.button(
                    f"Prepare {label}",
                    use_container_width=True,
                    key=f"prepare_{file_format}",
                ):
                    payload = {
                        "document_type": document_type or "Legal Document",
                        "content": st.session_state.document,
                        "terms": terms,
                        "format": file_format,
                    }

                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/export",
                            json=payload,
                            timeout=60,
                        )
                        if response.ok:
                            st.download_button(
                                label=f"⬇️ Download {label}",
                                data=response.content,
                                file_name=(
                                    f"LegalEase_"
                                    f"{(document_type or 'Legal_Document').replace(' ', '_')}"
                                    f".{file_format}"
                                ),
                                mime=response.headers.get(
                                    "content-type",
                                    "application/octet-stream",
                                ),
                                use_container_width=True,
                                key=f"download_{file_format}",
                            )
                        else:
                            try:
                                detail = response.json().get("detail", response.text)
                            except Exception:
                                detail = response.text
                            st.error(f"Export error: {detail}")
                    except requests.RequestException as exc:
                        st.error(f"Could not reach backend: {exc}")
    else:
        st.info("Your generated document will appear here.")

st.divider()
st.caption(
    "LegalEase is a document-drafting aid. It does not provide legal advice "
    "or guarantee enforceability."
)

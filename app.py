import streamlit as st
import html
import streamlit.components.v1 as components
from rag_pipeline import RAGPipeline

st.set_page_config(page_title="RAG PDF Chatbot", layout="centered")
st.title("RAG PDF Chatbot")

# ---- Global theme ----
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1a0630 0%, #0a0015 100%);
        color: #e6ccff;
    }
    h1 {
        color: #d9a3ff !important;
        text-shadow: 0 0 12px rgba(199, 125, 255, 0.8);
    }
    h2, h3 {
        color: #c77dff !important;
        text-shadow: 0 0 8px rgba(199, 125, 255, 0.6);
    }
    [data-testid="stFileUploader"] {
        background: #1f0838;
        border: 2px solid #6a2fb3;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 0 15px rgba(199, 125, 255, 0.4);
    }
    .stTextInput input {
        background-color: #1f0838;
        color: #f0d9ff;
        border: 2px solid #6a2fb3;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(199, 125, 255, 0.3);
    }
    .stTextInput input:focus {
        border: 2px solid #c77dff;
        box-shadow: 0 0 18px rgba(199, 125, 255, 0.8);
    }
    [data-testid="stExpander"] {
        background: #1f0838;
        border: 2px solid #6a2fb3;
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(199, 125, 255, 0.35);
    }
    .stAlert {
        background-color: #2a0a4a !important;
        color: #e6ccff !important;
        border: 1px solid #c77dff;
    }
    .stButton button {
        background-color: #3b0f66;
        color: #e6ccff;
        border: 2px solid #6a2fb3;
        border-radius: 10px;
    }
    .stButton button:hover {
        border: 2px solid #c77dff;
        box-shadow: 0 0 12px rgba(199, 125, 255, 0.6);
    }

    /* Chat bubbles */
    .chat-bubble-user {
        background: #2a0a4a;
        border: 2px solid #6a2fb3;
        border-radius: 14px;
        padding: 12px 18px;
        margin: 10px 0;
        color: #f0d9ff;
    }
    .chat-bubble-answer {
        background: #1f0838;
        border: 2px solid #c77dff;
        border-radius: 14px;
        padding: 14px 18px;
        margin: 4px 0 20px 0;
        color: #f0d9ff;
        box-shadow: 0 0 16px rgba(199, 125, 255, 0.35);
    }
    .chat-bubble-unknown {
        background: #14051f;
        border: 2px solid #4a2a5e;
        border-radius: 14px;
        padding: 14px 18px;
        margin: 4px 0 20px 0;
        color: #9a86a8;
        filter: grayscale(0.4);
    }
    </style>
""", unsafe_allow_html=True)


# ---- Custom glowing loader ----
def render_loader(text="Thinking..."):
    return components.html(f"""
        <style>
            .loader-wrap {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 0;
                font-family: sans-serif;
                color: #d9a3ff;
            }}
            .dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #c77dff;
                box-shadow: 0 0 10px rgba(199, 125, 255, 0.9);
                animation: pulse 1s infinite ease-in-out;
            }}
            .dot:nth-child(2) {{ animation-delay: 0.2s; }}
            .dot:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes pulse {{
                0%, 100% {{ transform: scale(0.6); opacity: 0.4; }}
                50% {{ transform: scale(1.2); opacity: 1; }}
            }}
        </style>
        <div class="loader-wrap">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            <span>{text}</span>
        </div>
    """, height=40)


# ---- Chunk carousel ----
def render_chunk_carousel(chunks):
    cards_html = ""
    for i, chunk in enumerate(chunks):
        safe_chunk = html.escape(chunk.replace("\n", " "))
        if len(safe_chunk) > 280:
            safe_chunk = safe_chunk[:280] + "..."
        cards_html += f'''
            <div class="chunk-card">
                <div class="chunk-label">Match #{i+1}</div>
                <p>{safe_chunk}</p>
            </div>
        '''

    html_code = f"""
    <style>
        .carousel-container {{
            background: linear-gradient(135deg, #2a0a4a, #1a0630);
            padding: 20px 0;
            border-radius: 16px;
            display: flex;
            justify-content: center;
        }}
        .carousel-track {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            overflow-y: auto;
            scroll-snap-type: y mandatory;
            height: 340px;
            width: 320px;
            padding: 90px 0;
            scrollbar-width: none;
        }}
        .carousel-track::-webkit-scrollbar {{ display: none; }}

        .chunk-card {{
            flex: 0 0 auto;
            width: 320px;
            height: 320px;
            scroll-snap-align: center;
            background: #3b0f66;
            border-radius: 14px;
            padding: 20px;
            color: #d9b3ff;
            font-family: sans-serif;
            font-size: 13px;
            line-height: 1.45;
            opacity: 0.35;
            transform: scale(0.8);
            filter: blur(1.5px);
            transition: all 0.35s ease;
            overflow: hidden;
            box-sizing: border-box;
            border: 2px solid transparent;
            position: relative;
        }}

        .chunk-label {{
            font-weight: bold;
            font-size: 11px;
            letter-spacing: 1px;
            color: #c77dff;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}

        .chunk-card p {{
            margin: 0;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 11;
            -webkit-box-orient: vertical;
        }}

        .chunk-card.active {{
            opacity: 1;
            transform: scale(1);
            filter: blur(0);
            color: #f0d9ff;
            border: 2px solid #c77dff;
            box-shadow: 0 0 20px 4px rgba(199, 125, 255, 0.7),
                        0 0 40px 10px rgba(199, 125, 255, 0.3);
        }}
    </style>

    <div class="carousel-container">
        <div class="carousel-track" id="track">
            {cards_html}
        </div>
    </div>

    <script>
        const track = document.getElementById('track');
        const cards = document.querySelectorAll('.chunk-card');

        function updateActive() {{
            const containerCenter = track.scrollTop + track.offsetHeight / 2;
            let closest = null;
            let closestDist = Infinity;

            cards.forEach(card => {{
                const cardCenter = card.offsetTop + card.offsetHeight / 2;
                const dist = Math.abs(containerCenter - cardCenter);
                if (dist < closestDist) {{
                    closestDist = dist;
                    closest = card;
                }}
            }});

            cards.forEach(c => c.classList.remove('active'));
            if (closest) closest.classList.add('active');
        }}

        track.addEventListener('scroll', updateActive);
        window.addEventListener('load', updateActive);
        setTimeout(updateActive, 200);
        setTimeout(updateActive, 500);
        setTimeout(updateActive, 1000);
    </script>
    """
    components.html(html_code, height=380, scrolling=False)


# ---- Pipeline setup ----
if "pipeline" not in st.session_state:
    st.session_state.pipeline = RAGPipeline()
    st.session_state.ingested = False
    st.session_state.history = []  # list of dicts: {question, answer, chunks, is_unknown}

pipeline = st.session_state.pipeline

# ---- File upload + ingestion ----
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None and not st.session_state.ingested:
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Reading and indexing your PDF..."):
        pipeline.ingest_pdf("uploaded.pdf")

    st.session_state.ingested = True
    st.success("PDF indexed! You can ask questions now.")

# ---- Reset / new PDF button ----
if st.button("Start over with a new PDF"):
    st.session_state.pipeline.clear()
    st.session_state.ingested = False
    st.session_state.history = []
    st.rerun()

# ---- Question input ----
if st.session_state.ingested:
    question = st.text_input("Ask a question about the PDF", key="question_input")

    if question:
        loader_placeholder = st.empty()
        with loader_placeholder:
            render_loader("Thinking...")

        context_chunks = pipeline.retrieve(question, top_k=5)
        answer = pipeline.ask(question, top_k=8)

        loader_placeholder.empty()

        is_unknown = any(
            phrase in answer.lower()
            for phrase in ["i don't know", "i'm not sure", "not included in the context",
                           "does not include", "don't have that information"]
        )

        st.session_state.history.append({
            "question": question,
            "answer": answer,
            "chunks": context_chunks,
            "is_unknown": is_unknown,
        })

    # ---- Render chat history ----
    for i, turn in enumerate(reversed(st.session_state.history)):
        st.markdown(f'<div class="chat-bubble-user">🧑 {turn["question"]}</div>', unsafe_allow_html=True)

        bubble_class = "chat-bubble-unknown" if turn["is_unknown"] else "chat-bubble-answer"
        icon = "❓" if turn["is_unknown"] else "✨"
        st.markdown(f'<div class="{bubble_class}">{icon} {turn["answer"]}</div>', unsafe_allow_html=True)

        with st.expander(f"Show source chunks for this answer"):
            render_chunk_carousel(turn["chunks"])
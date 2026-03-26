import time
import os
import json
import uuid
import requests
import streamlit as st

# =========================
# CONFIG
# =========================
CHAT_FILE = "chats.json"
MAX_CONTEXT_MESSAGES = 10

API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
    "Content-Type": "application/json"
}

MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPTS = {
    "General": "You are a helpful assistant.",
    "Programming": "You are a precise programming assistant. Use code blocks and concise explanations.",
    "Study": "You are a tutor. Explain step by step in simple language.",
    "Math": "Solve step by step with formulas and correct reasoning."
}

MODE_ICONS = {
    "General": "✦",
    "Programming": "⌨",
    "Study": "◎",
    "Math": "∑"
}

MODE_DESCRIPTIONS = {
    "General": "All-purpose assistant",
    "Programming": "Code & debugging",
    "Study": "Learn step by step",
    "Math": "Formulas & reasoning"
}

# =========================
# PREMIUM CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root & Reset ── */
:root {
    --bg:        #0a0a0f;
    --surface:   #111118;
    --surface2:  #18181f;
    --border:    #ffffff0f;
    --border2:   #ffffff18;
    --accent:    #c8f564;
    --accent2:   #7effd4;
    --text:      #f0f0f5;
    --muted:     #6b6b7d;
    --user-bg:   #1a1a24;
    --ai-bg:     #13131a;
    --glow:      rgba(200,245,100,0.12);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}

/* Main container */
[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
    font-family: 'Syne', sans-serif;
}

/* Hide default header/footer */
#MainMenu, footer, header { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border2) !important;
    min-width: 280px !important;
    max-width: 280px !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

.sidebar-inner {
    padding: 28px 20px 20px 20px;
}

/* Sidebar brand */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 0 24px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.brand-icon {
    width: 36px;
    height: 36px;
    background: var(--accent);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    color: #0a0a0f;
    font-weight: 800;
    flex-shrink: 0;
}

.brand-name {
    font-size: 17px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.3px;
}

.brand-sub {
    font-size: 11px;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.5px;
    line-height: 1;
    margin-top: 2px;
}

/* Sidebar section labels */
.sidebar-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 6px;
}

/* Mode cards */
.mode-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 20px;
}

.mode-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 12px;
    cursor: pointer;
    transition: all 0.2s;
}

.mode-card:hover {
    border-color: var(--border2);
    background: #1e1e28;
}

.mode-card.active {
    border-color: var(--accent);
    background: rgba(200,245,100,0.06);
}

.mode-icon {
    font-size: 16px;
    margin-bottom: 4px;
}

.mode-name {
    font-size: 12px;
    font-weight: 600;
    color: var(--text);
}

.mode-desc {
    font-size: 10px;
    color: var(--muted);
    margin-top: 1px;
}

/* Chat list */
.chat-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    cursor: pointer;
    border: 1px solid transparent;
    margin-bottom: 4px;
    transition: all 0.15s;
}

.chat-item:hover {
    background: var(--surface2);
    border-color: var(--border);
}

.chat-item.active {
    background: rgba(200,245,100,0.07);
    border-color: rgba(200,245,100,0.25);
}

.chat-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--muted);
    flex-shrink: 0;
}

.chat-item.active .chat-dot {
    background: var(--accent);
    box-shadow: 0 0 6px var(--accent);
}

.chat-title {
    font-size: 13px;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
}

/* Streamlit selectbox override */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSelectbox"] label {
    color: var(--muted) !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    font-family: 'Syne', sans-serif !important;
}

/* Buttons */
[data-testid="stButton"] button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    letter-spacing: 0.2px !important;
}

[data-testid="stButton"] button:hover {
    background: rgba(200,245,100,0.08) !important;
    border-color: rgba(200,245,100,0.35) !important;
    color: var(--accent) !important;
}

/* ── Main header ── */
.main-header {
    text-align: center;
    padding: 48px 0 32px;
    position: relative;
}

.header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(200,245,100,0.08);
    border: 1px solid rgba(200,245,100,0.2);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 1px;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace;
    margin-bottom: 20px;
}

.header-dot {
    width: 6px;
    height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

.main-title {
    font-size: 52px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -2px;
    line-height: 1;
    margin-bottom: 12px;
}

.main-title span {
    color: var(--accent);
}

.main-sub {
    font-size: 15px;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-weight: 300;
}

/* Active mode pill */
.mode-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface2);
    border: 1px solid var(--border2);
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 12px;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    margin-top: 16px;
}

.mode-pill-dot {
    width: 6px;
    height: 6px;
    background: var(--accent2);
    border-radius: 50%;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* User messages */
[data-testid="stChatMessage"][data-testid*="user"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: transparent !important;
}

/* Override chat message containers */
.stChatMessage {
    background: transparent !important;
}

[data-testid="stChatMessageContent"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 14.5px !important;
    line-height: 1.7 !important;
    color: var(--text) !important;
}

/* Avatar */
[data-testid="chatAvatarIcon-user"] {
    background: var(--user-bg) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: rgba(200,245,100,0.1) !important;
    border: 1px solid rgba(200,245,100,0.3) !important;
    border-radius: 10px !important;
    color: var(--accent) !important;
}

/* Message bubble wrapping */
.stChatMessageContent {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
}

/* Code blocks */
code {
    font-family: 'DM Mono', monospace !important;
    background: #0d0d14 !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    padding: 2px 7px !important;
    font-size: 13px !important;
    color: var(--accent2) !important;
}

pre {
    background: #0d0d14 !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
}

pre code {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    color: #b8ffa8 !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 16px !important;
    padding: 4px !important;
    box-shadow: 0 0 0 1px var(--border), 0 8px 32px rgba(0,0,0,0.4) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: rgba(200,245,100,0.3) !important;
    box-shadow: 0 0 0 1px rgba(200,245,100,0.1), 0 8px 32px rgba(0,0,0,0.5), 0 0 20px var(--glow) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    caret-color: var(--accent) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--muted) !important;
}

[data-testid="stChatInput"] button {
    background: var(--accent) !important;
    border-radius: 10px !important;
    border: none !important;
    color: #0a0a0f !important;
    width: 36px !important;
    height: 36px !important;
    min-height: unset !important;
    padding: 0 !important;
}

[data-testid="stChatInput"] button:hover {
    background: #d4f87a !important;
    border: none !important;
    color: #0a0a0f !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
    margin: 8px 0 !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    max-width: 420px;
    margin: 0 auto;
}

.empty-glyph {
    font-size: 40px;
    margin-bottom: 16px;
    opacity: 0.4;
}

.empty-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}

.empty-sub {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.6;
}

.suggestion-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 28px;
    text-align: left;
}

.suggestion-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 14px;
    cursor: pointer;
    transition: all 0.15s;
}

.suggestion-card:hover {
    border-color: var(--border2);
    background: #1c1c26;
}

.suggestion-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 3px;
}

.suggestion-sub {
    font-size: 11px;
    color: var(--muted);
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* Main block padding */
.block-container {
    padding: 0 2rem 2rem 2rem !important;
    max-width: 820px !important;
}

/* Streamlit markdown inside chat */
[data-testid="stMarkdownContainer"] p {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
    font-size: 14.5px !important;
    line-height: 1.7 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# GROQ FUNCTION
# =========================
def query_groq(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            return "⚠️ Server busy or API limit reached. Please try again."
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except:
        return "⚠️ Network error. Please check your connection."


# =========================
# LOAD / SAVE
# =========================
def load_chats():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_chats():
    with open(CHAT_FILE, "w") as f:
        json.dump(st.session_state.chats, f, indent=2)


# =========================
# SESSION INIT
# =========================
if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current_chat" not in st.session_state:
    cid = str(uuid.uuid4())
    st.session_state.chats[cid] = {
        "title": "New Chat",
        "system": SYSTEM_PROMPTS["General"],
        "messages": []
    }
    st.session_state.current_chat = cid

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "General"


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-inner">
        <div class="sidebar-brand">
            <div class="brand-icon">T</div>
            <div>
                <div class="brand-name">ThinkBot</div>
                <div class="brand-sub">POWERED BY GROQ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 20px;">', unsafe_allow_html=True)

    # Mode selector
    st.markdown('<div class="sidebar-label">Mode</div>', unsafe_allow_html=True)
    selected_mode = st.selectbox(
        label="Mode",
        options=list(SYSTEM_PROMPTS.keys()),
        index=list(SYSTEM_PROMPTS.keys()).index(st.session_state.selected_mode),
        label_visibility="collapsed"
    )
    st.session_state.selected_mode = selected_mode

    # Mode info card
    st.markdown(f"""
    <div style="background: rgba(200,245,100,0.05); border: 1px solid rgba(200,245,100,0.15);
                border-radius: 10px; padding: 10px 14px; margin: 8px 0 20px 0;">
        <div style="font-size: 20px; margin-bottom: 4px;">{MODE_ICONS[selected_mode]}</div>
        <div style="font-size: 12px; font-weight: 600; color: #f0f0f5;">{selected_mode}</div>
        <div style="font-size: 11px; color: #6b6b7d; margin-top: 2px;">{MODE_DESCRIPTIONS[selected_mode]}</div>
    </div>
    """, unsafe_allow_html=True)

    # New chat button
    st.markdown('<div class="sidebar-label">Actions</div>', unsafe_allow_html=True)
    if st.button("✦  New conversation", use_container_width=True):
        cid = str(uuid.uuid4())
        st.session_state.chats[cid] = {
            "title": "New Chat",
            "system": SYSTEM_PROMPTS[selected_mode],
            "messages": []
        }
        st.session_state.current_chat = cid
        save_chats()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history
    st.markdown('<div class="sidebar-label">History</div>', unsafe_allow_html=True)

    chat_ids = list(st.session_state.chats.keys())
    for cid in reversed(chat_ids[-12:]):
        chat_data = st.session_state.chats[cid]
        is_active = cid == st.session_state.current_chat
        title = chat_data.get("title", "New Chat")
        active_class = "active" if is_active else ""

        if st.button(
            f"{'●' if is_active else '○'}  {title[:28]}{'…' if len(title) > 28 else ''}",
            key=f"chat_{cid}",
            use_container_width=True
        ):
            st.session_state.current_chat = cid
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# MAIN AREA
# =========================
chat = st.session_state.chats[st.session_state.current_chat]
messages = chat["messages"]
chat["system"] = SYSTEM_PROMPTS[selected_mode]

# Header
st.markdown(f"""
<div class="main-header">
    <div class="header-badge">
        <div class="header-dot"></div>
        Online · Groq LLaMA 3.1
    </div>
    <div class="main-title">Think<span>Bot</span></div>
    <div class="main-sub">fast intelligence, zero friction</div>
    <div class="mode-pill">
        <div class="mode-pill-dot"></div>
        {MODE_ICONS[selected_mode]} {selected_mode} mode active
    </div>
</div>
""", unsafe_allow_html=True)

# Messages or empty state
if not messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-glyph">✦</div>
        <div class="empty-title">Start a conversation</div>
        <div class="empty-sub">Ask anything — code, math, concepts, or just chat. ThinkBot is ready.</div>
        <div class="suggestion-grid">
            <div class="suggestion-card">
                <div class="suggestion-label">Debug my code</div>
                <div class="suggestion-sub">Paste code & explain the bug</div>
            </div>
            <div class="suggestion-card">
                <div class="suggestion-label">Explain a concept</div>
                <div class="suggestion-sub">Simple, clear explanations</div>
            </div>
            <div class="suggestion-card">
                <div class="suggestion-label">Solve math</div>
                <div class="suggestion-sub">Step-by-step solutions</div>
            </div>
            <div class="suggestion-card">
                <div class="suggestion-label">Study with me</div>
                <div class="suggestion-sub">Learn any topic fast</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Input
user_input = st.chat_input("Message ThinkBot...")

if user_input:
    if not messages:
        chat["title"] = user_input[:40]

    messages.append({"role": "user", "content": user_input})
    save_chats()

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(
            '<span style="color:#6b6b7d; font-family:\'DM Mono\',monospace; font-size:13px;">⠋ Thinking...</span>',
            unsafe_allow_html=True
        )

        trimmed = messages[-MAX_CONTEXT_MESSAGES:]
        groq_messages = [
            {"role": "system", "content": chat["system"]},
            *trimmed
        ]

        response = query_groq(groq_messages)

        full_response = ""
        for char in response:
            full_response += char
            placeholder.markdown(full_response + "▌")
            time.sleep(0.008)

        placeholder.markdown(full_response)

    messages.append({"role": "assistant", "content": response})
    save_chats()

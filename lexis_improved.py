import streamlit as st
from dotenv import load_dotenv
import tempfile
import os
import shutil
import html
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# ─────────────────────────────────────────────────────────────
#  LOGGING SETUP
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  ENVIRONMENT & PAGE CONFIG
# ─────────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["MISTRAL_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

st.set_page_config(
    page_title="Lexis · AI Book Assistant",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  ENHANCED CSS WITH IMPROVED AESTHETICS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Fira+Code:wght@400;500&family=Nunito:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --navy: #080d1a;
    --navy-mid: #0d1425;
    --navy-card: #111828;
    --navy-lift: #161f32;
    --navy-bright: #1a2847;
    --violet: #7c6af7;
    --violet-dim: rgba(124,106,247,0.12);
    --violet-glow: rgba(124,106,247,0.06);
    --violet-bdr: rgba(124,106,247,0.22);
    --violet-hov: rgba(124,106,247,0.42);
    --violet-bright: #9d89ff;
    --teal: #4ecdc4;
    --teal-dim: rgba(78,205,196,0.15);
    --emerald: #52c97a;
    --emerald-dim: rgba(82,201,122,0.12);
    --amber: #f0a847;
    --amber-dim: rgba(240,168,71,0.12);
    --crimson: #e05a6a;
    --crimson-dim: rgba(224,90,106,0.12);
    --ivory: #eae6dc;
    --ivory-dim: #a09b8f;
    --ivory-muted: #6b6560;
    --border: rgba(124,106,247,0.15);
    --border-soft: rgba(255,255,255,0.05);
    --border-bright: rgba(124,106,247,0.3);
    --success: #52c97a;
    --warning: #f0a847;
    --danger: #e05a6a;
    --shadow-sm: 0 4px 12px rgba(0,0,0,0.15);
    --shadow-md: 0 8px 24px rgba(0,0,0,0.25);
    --shadow-lg: 0 16px 40px rgba(0,0,0,0.35);
}

*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--navy) !important;
    font-family: 'Nunito', sans-serif;
    color: var(--ivory);
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 40% at 10% 0%, rgba(124,106,247,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 90% 100%, rgba(78,205,196,0.06) 0%, transparent 55%),
        radial-gradient(ellipse 100% 100% at 50% 50%, rgba(8,13,26,1) 20%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stMain"] {
    background: transparent !important;
}

.block-container {
    padding: 1.2rem 1.8rem 5rem !important;
    max-width: 1000px !important;
    margin: 0 auto;
}

/* ── Sidebar ────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 1.2rem 0.9rem 2rem;
}

.sb-brand {
    text-align: center;
    padding: 0.5rem 0 1.3rem;
    border-bottom: 1px solid var(--border-soft);
    margin-bottom: 1.1rem;
    position: relative;
}

.sb-brand::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 10%;
    right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--violet), transparent);
    opacity: 0.5;
}

.sb-logo {
    font-size: 2.5rem;
    margin-bottom: 8px;
    display: block;
    filter: drop-shadow(0 0 20px rgba(124,106,247,0.5));
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
}

.sb-brand h2 {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 1.4rem;
    color: var(--ivory);
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}

.sb-brand p {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: var(--violet-bright);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    opacity: 0.8;
}

.sb-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(124,106,247,0.65);
    margin: 1.2rem 0 0.5rem;
    padding-left: 2px;
    font-weight: 600;
}

/* ── File pills ────────────────────────────────────── */
.file-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--violet-dim);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 7px 12px;
    margin-bottom: 6px;
    font-size: 0.75rem;
    color: var(--ivory);
    word-break: break-word;
    line-height: 1.3;
    transition: all 0.2s ease;
}

.file-pill:hover {
    background: var(--violet-dim);
    border-color: var(--violet-bright);
    box-shadow: 0 0 12px rgba(124,106,247,0.2);
}

.file-pill .fi {
    color: var(--violet-bright);
    flex-shrink: 0;
    font-size: 1rem;
}

/* ── KB status badge ────────────────────────────────– */
.kb-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}

.kb-badge:hover {
    border-color: var(--border-bright);
    background: var(--navy-lift);
}

.kb-badge .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pulse-dot 2s ease-in-out infinite;
}

.dot-green {
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
}

.dot-orange {
    background: var(--warning);
    box-shadow: 0 0 8px var(--warning);
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Buttons ───────────────────────────────────────– */
.stButton > button {
    width: 100% !important;
    background: var(--violet-dim) !important;
    border: 1px solid var(--border) !important;
    color: var(--ivory) !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    padding: 0.58rem 1rem !important;
    margin-bottom: 6px !important;
    transition: all 0.25s ease !important;
    text-align: center !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    background: var(--violet) !important;
    border-color: var(--violet-bright) !important;
    color: var(--navy) !important;
    box-shadow: 0 0 20px rgba(124,106,247,0.25) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── File uploader ──────────────────────────────────– */
[data-testid="stFileUploader"] {
    background: var(--navy-card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    transition: all 0.2s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--violet-bright) !important;
    background: rgba(124,106,247,0.05) !important;
}

/* ── Selectbox ──────────────────────────────────────– */
[data-testid="stSelectbox"] > div > div {
    background: var(--navy-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--ivory) !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.86rem !important;
}

/* ── Page header ───────────────────────────────────– */
.page-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 1.5rem 1.8rem;
    background: linear-gradient(135deg, var(--navy-card) 0%, var(--navy-lift) 100%);
    border: 1px solid var(--border-bright);
    border-radius: 18px;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
}

.page-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--violet), transparent);
    opacity: 0.6;
}

.ph-icon {
    font-size: 2.2rem;
    filter: drop-shadow(0 0 14px rgba(124,106,247,0.5));
    flex-shrink: 0;
}

.ph-title {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 1.6rem;
    color: var(--ivory);
    letter-spacing: 0.03em;
    line-height: 1;
}

.ph-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--violet-bright);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.8;
}

.ph-right {
    margin-left: auto;
}

.status-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(82,201,122,0.1);
    border: 1px solid rgba(82,201,122,0.3);
    border-radius: 22px;
    padding: 6px 15px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--success);
    letter-spacing: 0.12em;
    white-space: nowrap;
    font-weight: 600;
}

.pulse {
    width: 7px;
    height: 7px;
    background: var(--success);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--success);
    animation: pulse-anim 2s ease-in-out infinite;
}

@keyframes pulse-anim {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Section heading ───────────────────────────────– */
.sec-head {
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1rem;
    color: var(--violet-bright);
    margin: 1.4rem 0 0.8rem;
    font-weight: 600;
}

.sec-head::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    border-radius: 2px;
}

.sec-head-icon {
    font-size: 1.1rem;
}

/* ── Divider ────────────────────────────────────────– */
.vdivider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1rem 0;
    opacity: 0.6;
}

/* ── Chat bubbles ───────────────────────────────────– */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 0.5rem 0;
}

.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    animation: slidein 0.3s ease;
}

.msg-row.user {
    justify-content: flex-end;
}

.msg-row.bot {
    justify-content: flex-start;
}

@keyframes slidein {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.av {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3));
}

.av-user {
    background: linear-gradient(135deg, #3d2a9f, #1a1060);
    border: 1px solid rgba(157,137,255,0.4);
}

.av-bot {
    background: linear-gradient(135deg, #1a2847, #0d1425);
    border: 1px solid var(--border-bright);
    box-shadow: 0 0 14px rgba(124,106,247,0.2);
}

.bubble {
    max-width: 78%;
    padding: 14px 18px;
    font-size: 0.91rem;
    line-height: 1.68;
    border-radius: 16px;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}

.bubble.user {
    background: linear-gradient(135deg, #2d1f8a, #1a1060);
    color: var(--ivory);
    border: 1px solid rgba(124,106,247,0.35);
    border-radius: 16px 16px 4px 16px;
}

.bubble.user:hover {
    box-shadow: 0 6px 20px rgba(124,106,247,0.2);
}

.bubble.bot {
    background: var(--navy-card);
    color: var(--ivory);
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
}

.bubble.bot:hover {
    border-color: var(--border-bright);
}

.bubble .ts {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: rgba(160,155,143,0.45);
    margin-top: 8px;
    text-align: right;
}

/* ── Welcome state ──────────────────────────────────– */
.welcome {
    text-align: center;
    padding: 4rem 1.5rem 3rem;
}

.welcome .wi {
    font-size: 4rem;
    margin-bottom: 1.2rem;
    display: block;
    filter: drop-shadow(0 0 24px rgba(124,106,247,0.35));
    animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-12px); }
}

.welcome h3 {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 1.8rem;
    color: var(--ivory);
    margin-bottom: 12px;
    letter-spacing: 0.02em;
}

.welcome p {
    font-size: 0.92rem;
    color: var(--ivory-dim);
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.7;
}

.hint-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    margin-top: 1.5rem;
}

.hint {
    background: var(--violet-dim);
    border: 1px solid var(--border);
    color: rgba(160,155,143,0.8);
    padding: 7px 16px;
    border-radius: 24px;
    font-size: 0.78rem;
    transition: all 0.2s ease;
    cursor: default;
}

.hint:hover {
    border-color: var(--violet-bright);
    background: rgba(124,106,247,0.18);
    color: var(--ivory);
}

/* ── Confidence bar ────────────────────────────────– */
.conf-wrap {
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 15px 18px;
    margin-bottom: 1.2rem;
    transition: all 0.2s ease;
}

.conf-wrap:hover {
    border-color: var(--border-bright);
    background: var(--navy-lift);
}

.conf-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(124,106,247,0.7);
    margin-bottom: 10px;
    font-weight: 600;
}

.conf-track {
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    height: 8px;
    overflow: hidden;
    border: 1px solid rgba(124,106,247,0.1);
}

.conf-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.conf-val {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 1.2rem;
    margin-top: 8px;
}

/* ── Source cards ──────────────────────────────────– */
.src-card {
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--violet);
    border-radius: 0 12px 12px 0;
    padding: 14px 17px;
    margin-bottom: 10px;
    transition: all 0.25s ease;
}

.src-card:hover {
    border-color: var(--violet-bright);
    border-left-color: var(--violet-bright);
    background: var(--navy-lift);
    box-shadow: 0 0 20px rgba(124,106,247,0.12);
}

.src-name {
    font-family: 'Playfair Display', serif;
    font-size: 0.85rem;
    color: var(--violet-bright);
    font-weight: 600;
    margin-bottom: 4px;
}

.src-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--ivory-dim);
    letter-spacing: 0.08em;
    margin-bottom: 8px;
    opacity: 0.7;
}

.src-snip {
    font-size: 0.81rem;
    color: #8a8075;
    line-height: 1.6;
    font-style: italic;
}

/* ── Expandable sections ────────────────────────────– */
.expandable-btn {
    width: 100% !important;
    background: var(--navy-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--ivory) !important;
    padding: 12px 15px !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 8px !important;
    transition: all 0.2s ease !important;
}

.expandable-btn:hover {
    background: var(--navy-lift) !important;
    border-color: var(--border-bright) !important;
}

.expand-content {
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 15px;
    margin-bottom: 12px;
    animation: expand 0.3s ease;
}

@keyframes expand {
    from {
        opacity: 0;
        max-height: 0;
    }
    to {
        opacity: 1;
        max-height: 1000px;
    }
}

/* ── Chat input override ───────────────────────────– */
[data-testid="stChatInput"] {
    background: var(--navy-card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 16px !important;
    box-shadow: 0 0 0 0 transparent !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--violet-bright) !important;
    box-shadow: 0 0 32px rgba(124,106,247,0.15) !important;
    background: var(--navy-lift) !important;
}

[data-testid="stChatInput"] textarea {
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.92rem !important;
    color: var(--ivory) !important;
    background: transparent !important;
}

/* ── Spinner ───────────────────────────────────────– */
[data-testid="stSpinner"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    color: var(--violet-bright) !important;
    letter-spacing: 0.1em;
}

/* ── Alerts ────────────────────────────────────────– */
[data-testid="stAlert"] {
    background: var(--navy-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--ivory) !important;
}

/* ── Metrics ───────────────────────────────────────– */
.metric-card {
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    transition: all 0.2s ease;
}

.metric-card:hover {
    border-color: var(--border-bright);
    background: var(--navy-lift);
}

.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--violet-bright);
}

.metric-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--ivory-dim);
    margin-top: 4px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Footer ────────────────────────────────────────– */
.footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255,255,255,0.05);
}

.footer span {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.59rem;
    color: rgba(100,100,130,0.5);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* ── Scrollbar ──────────────────────────────────────– */
::-webkit-scrollbar {
    width: 5px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(124,106,247,0.25);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(124,106,247,0.45);
}

/* ── Hide Streamlit chrome ──────────────────────────– */
#MainMenu, footer {
    visibility: hidden;
}

[data-testid="stDecoration"] {
    display: none;
}

[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    z-index: 999999 !important;
}

[data-testid="stSidebarCollapsedControl"] button {
    visibility: visible !important;
    background: var(--navy-mid) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 0 10px 10px 0 !important;
    color: var(--ivory) !important;
    box-shadow: 2px 0 16px rgba(124,106,247,0.25) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebarCollapsedControl"] button:hover {
    background: var(--violet-dim) !important;
    border-color: var(--violet-bright) !important;
}

[data-testid="stSidebarCollapsedControl"] svg {
    fill: var(--ivory) !important;
    color: var(--ivory) !important;
}

/* ── Loading animation ──────────────────────────────– */
.loading-dots {
    display: inline-block;
}

.loading-dots span {
    display: inline-block;
    background: var(--violet-bright);
    border-radius: 50%;
    width: 5px;
    height: 5px;
    margin: 0 3px;
    animation: loading 1.4s infinite;
}

.loading-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes loading {
    0%, 60%, 100% {
        opacity: 0.3;
        transform: translateY(0);
    }
    30% {
        opacity: 1;
        transform: translateY(-10px);
    }
}

/* ── Responsive ────────────────────────────────────– */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 1rem 3rem !important;
    }
    
    .bubble {
        max-width: 90%;
    }
    
    .page-header {
        flex-direction: column;
        text-align: center;
    }
    
    .ph-right {
        margin-left: 0;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  CONFIGURATION & CONSTANTS
# ─────────────────────────────────────────────────────────────
CONFIG = {
    "chunk_size": 1500,
    "chunk_overlap": 400,
    "retriever_k": 8,
    "retriever_fetch_k": 25,
    "retriever_lambda": 0.7,
    "llm_temperature": 0.2,
    "llm_model": "mistral-small-2506",
    "embedding_model": "mistral-embed",
    "history_limit": 10,
    "max_context_length": 5000,
}

CHAT_HISTORY_FILE = Path("data/chat_history.json")
ANALYTICS_FILE = Path("data/analytics.json")

# ─────────────────────────────────────────────────────────────
#  GUARD: API KEY
# ─────────────────────────────────────────────────────────────
if not api_key:
    st.error("⚠️ MISTRAL_API_KEY not found. Add it to your .env file (local) or Streamlit Cloud Secrets (deployed).")
    st.stop()

os.environ["MISTRAL_API_KEY"] = api_key
logger.info("✅ API key configured successfully")

# ─────────────────────────────────────────────────────────────
#  SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "kb_ready" not in st.session_state:
    st.session_state.kb_ready = os.path.exists("chroma_db")
if "show_memory" not in st.session_state:
    st.session_state.show_memory = False
if "show_sources" not in st.session_state:
    st.session_state.show_sources = False
if "kb_stats" not in st.session_state:
    st.session_state.kb_stats = {"docs": 0, "chunks": 0, "last_updated": None}

# ─────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def ts_now() -> str:
    """Get current timestamp"""
    return datetime.now().strftime("%H:%M")

def safe_text(text: str) -> str:
    """HTML escape text safely"""
    return html.escape(text)

def safe_snippet(text: str, length: int = 240) -> str:
    """Create safe text snippet"""
    return html.escape(text[:length])

def semantic_score_doc(doc: Document, query_words: set, query: str) -> float:
    """
    Enhanced document scoring considering:
    - Keyword overlap
    - Query length vs matched content
    - Proximity of matches
    """
    content_lower = doc.page_content.lower()
    content_words = set(content_lower.split())
    
    # Word overlap score
    overlap = len(query_words & content_words)
    if len(query_words) == 0:
        return 0
    
    overlap_ratio = overlap / len(query_words)
    
    # Check if multiple query words appear close together
    proximity_bonus = 0
    for word in query_words:
        if word in content_lower:
            # Find position and check density
            idx = content_lower.find(word)
            window = content_lower[max(0, idx-200):min(len(content_lower), idx+200)]
            matches_in_window = sum(1 for w in query_words if w in window)
            proximity_bonus += matches_in_window * 0.1
    
    # Length consideration (longer content relevant to short query might be less relevant)
    length_factor = min(len(query.split()) / max(len(content_lower.split()) / 20, 1), 1)
    
    return overlap_ratio + proximity_bonus + length_factor * 0.2

def improved_confidence_score(docs: List[Document], query: str, overlap_percent: float) -> int:
    """
    Improved confidence scoring based on:
    - Document quality (semantic score)
    - Retrieval overlap
    - Document count and diversity
    """
    if not docs:
        return 0
    
    query_words = set(query.lower().split())
    
    # Calculate semantic score for all docs
    doc_scores = [semantic_score_doc(d, query_words, query) for d in docs]
    avg_semantic = sum(doc_scores) / len(doc_scores) if doc_scores else 0
    
    # Confidence calculation
    semantic_confidence = min(int(avg_semantic * 60), 60)
    retrieval_confidence = min(int(overlap_percent * 30), 30)
    diversity_bonus = min(len(set(d.metadata.get("source") for d in docs)) * 5, 10)
    
    return min(semantic_confidence + retrieval_confidence + diversity_bonus, 100)

def format_context_with_structure(docs: List[Document]) -> Tuple[str, float]:
    """
    Format context with better structure and calculate overlap percentage
    """
    if not docs:
        return "", 0
    
    # Group by source
    by_source = {}
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(doc)
    
    # Build structured context
    context_parts = []
    total_words = 0
    retrieved_words = 0
    
    for source, source_docs in by_source.items():
        page = source_docs[0].metadata.get('page', '?')
        context_parts.append(f"[Document: {source} • Page {page}]")
        context_parts.append("─" * 50)
        
        for doc in source_docs:
            context_parts.append(doc.page_content)
            retrieved_words += len(doc.page_content.split())
        
        context_parts.append("")
    
    context = "\n".join(context_parts)
    
    # Calculate overlap (rough estimate)
    total_words = sum(len(d.page_content.split()) for d in docs)
    overlap_percent = (retrieved_words / max(total_words, 1)) * 100
    
    return context[:CONFIG["max_context_length"]], min(overlap_percent / 100, 1.0)

def load_chat_history() -> List[Dict]:
    """Load chat history from file"""
    try:
        if CHAT_HISTORY_FILE.exists():
            with open(CHAT_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load chat history: {e}")
    return []

def save_chat_history():
    """Save chat history to file"""
    try:
        CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(st.session_state.chat_history[-CONFIG["history_limit"]:], f)
    except Exception as e:
        logger.warning(f"Could not save chat history: {e}")

def log_analytics(query: str, confidence: int, doc_count: int):
    """Log usage analytics"""
    try:
        ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        analytics = []
        if ANALYTICS_FILE.exists():
            with open(ANALYTICS_FILE, 'r') as f:
                analytics = json.load(f)
        
        analytics.append({
            "timestamp": datetime.now().isoformat(),
            "query_length": len(query.split()),
            "confidence": confidence,
            "docs_retrieved": doc_count
        })
        
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(analytics[-1000:], f)  # Keep last 1000 queries
    except Exception as e:
        logger.warning(f"Could not log analytics: {e}")

# ─────────────────────────────────────────────────────────────
#  CACHED RESOURCES
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Get or create embeddings model"""
    try:
        logger.info(f"Loading embeddings model: {CONFIG['embedding_model']}")
        return MistralAIEmbeddings(model=CONFIG["embedding_model"])
    except Exception as e:
        logger.error(f"Failed to load embeddings: {e}")
        st.error(f"❌ Failed to load embeddings model: {str(e)}")
        st.stop()

@st.cache_resource(show_spinner=False)
def get_llm():
    """Get or create LLM"""
    try:
        logger.info(f"Loading LLM model: {CONFIG['llm_model']}")
        return ChatMistralAI(
            model=CONFIG["llm_model"],
            temperature=CONFIG["llm_temperature"],
            max_tokens=2048
        )
    except Exception as e:
        logger.error(f"Failed to load LLM: {e}")
        st.error(f"❌ Failed to load language model: {str(e)}")
        st.stop()

@st.cache_resource(show_spinner=False)
def get_vectorstore(_embeddings):
    """Get or create vector store"""
    try:
        if not os.path.exists("chroma_db"):
            return None
        logger.info("Loading vector store from disk")
        return Chroma(
            persist_directory="chroma_db",
            embedding_function=_embeddings,
        )
    except Exception as e:
        logger.error(f"Failed to load vector store: {e}")
        return None

# ─────────────────────────────────────────────────────────────
#  SIDEBAR - FIXED (NO DUPLICATES)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    
    # Brand
    st.markdown("""
    <div class="sb-brand">
        <span class="sb-logo">📖</span>
        <h2>Lexis</h2>
        <p>AI Book Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="vdivider">', unsafe_allow_html=True)

    # ── DOCUMENT UPLOAD SECTION (SINGLE) ────────────────────
    st.markdown('<p class="sb-label">📂 Upload Documents</p>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop PDFs here",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="pdf_uploader"
    )

    if uploaded_files:
        for f in uploaded_files:
            st.markdown(
                f'<div class="file-pill"><span class="fi">📄</span>{safe_text(f.name)}</div>',
                unsafe_allow_html=True,
            )

        if st.button("⚙️  Build Knowledge Base", use_container_width=True):
            with st.spinner("📚 Indexing documents…"):
                try:
                    all_docs = []
                    embeddings = get_embeddings()

                    # Load and process PDFs
                    for uf in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(uf.read())
                            tmp_path = tmp.name
                        try:
                            loader = PyPDFLoader(tmp_path)
                            docs = loader.load()
                            logger.info(f"Loaded {len(docs)} pages from {uf.name}")
                            
                            for doc in docs:
                                doc.metadata["source"] = uf.name
                            all_docs.extend(docs)
                        except Exception as e:
                            logger.error(f"Error loading {uf.name}: {e}")
                            st.warning(f"⚠️ Error loading {uf.name}: {str(e)}")
                        finally:
                            os.unlink(tmp_path)

                    if not all_docs:
                        st.error("❌ No documents loaded. Check file format.")
                        st.stop()

                    # Split documents
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=CONFIG["chunk_size"],
                        chunk_overlap=CONFIG["chunk_overlap"],
                        separators=["\n\n", "\n", ". ", " ", ""]
                    )
                    chunks = splitter.split_documents(all_docs)
                    logger.info(f"Created {len(chunks)} chunks from {len(all_docs)} pages")

                    # Store in vector database
                    if os.path.exists("chroma_db"):
                        vs = Chroma(
                            persist_directory="chroma_db",
                            embedding_function=embeddings,
                        )
                        vs.add_documents(chunks)
                        logger.info(f"Added {len(chunks)} chunks to existing database")
                    else:
                        Chroma.from_documents(
                            documents=chunks,
                            embedding=embeddings,
                            persist_directory="chroma_db",
                        )
                        logger.info(f"Created new database with {len(chunks)} chunks")

                    # Update session state
                    get_vectorstore.clear()
                    st.session_state.kb_ready = True
                    st.session_state.kb_stats = {
                        "docs": len(all_docs),
                        "chunks": len(chunks),
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }

                    st.success(f"✅ {len(chunks)} chunks indexed from {len(uploaded_files)} file(s).")
                    logger.info("Knowledge base built successfully")
                    
                except Exception as e:
                    logger.error(f"Error building knowledge base: {e}")
                    st.error(f"❌ Error building knowledge base: {str(e)}")

    st.markdown('<hr class="vdivider">', unsafe_allow_html=True)

    # ── KNOWLEDGE BASE STATUS ──────────────────────────────
    st.markdown('<p class="sb-label">🗄 Knowledge Base</p>', unsafe_allow_html=True)

    if st.session_state.kb_ready:
        st.markdown("""
        <div class="kb-badge">
            <div class="dot dot-green"></div>
            <span style="color:#52c97a;">Ready</span>
        </div>""", unsafe_allow_html=True)
        
        # Display KB stats
        if st.session_state.kb_stats["docs"] > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{st.session_state.kb_stats['docs']}</div>
                    <div class="metric-lbl">Documents</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{st.session_state.kb_stats['chunks']}</div>
                    <div class="metric-lbl">Chunks</div>
                </div>
                """, unsafe_allow_html=True)

        if st.button("🗑️  Reset Knowledge Base", use_container_width=True):
            try:
                if os.path.exists("chroma_db"):
                    shutil.rmtree("chroma_db")
                get_vectorstore.clear()
                st.session_state.kb_ready = False
                st.session_state.chat_history = []
                st.session_state.kb_stats = {"docs": 0, "chunks": 0, "last_updated": None}
                logger.info("Knowledge base reset")
                st.rerun()
            except Exception as e:
                logger.error(f"Error resetting knowledge base: {e}")
                st.error(f"❌ Error resetting knowledge base: {str(e)}")
    else:
        st.markdown("""
        <div class="kb-badge">
            <div class="dot dot-orange"></div>
            <span style="color:#f0a847;">Not ready</span>
        </div>""", unsafe_allow_html=True)
        st.info("📖 Upload PDFs to begin")

    st.markdown('<hr class="vdivider">', unsafe_allow_html=True)

    # ── CHAT MEMORY ────────────────────────────────────────
    st.markdown('<p class="sb-label">🧠 Memory</p>', unsafe_allow_html=True)

    if st.button("📜 Chat History", use_container_width=True):
        st.session_state.show_memory = not st.session_state.show_memory

    if st.session_state.show_memory:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history[-6:]:
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                st.markdown(
                    f"""<div style="background:#111828;padding:8px;border-radius:8px;
                    margin-bottom:6px;border-left:3px solid var(--violet);">
                        <b style="color:var(--violet-bright);">{role_icon} {msg['role'].upper()}</b><br>
                        <span style="font-size:12px;color:var(--ivory-dim);">
                        {safe_text(msg['content'][:110])}...
                        </span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No chat history")

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        logger.info("Chat history cleared")
        st.rerun()

    st.markdown('<hr class="vdivider">', unsafe_allow_html=True)

    # ── MODEL CONFIGURATION ────────────────────────────────
    st.markdown("""
    <p class="sb-label" style="margin-top:0;">⚙️ Configuration</p>
    <p style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
              color:#3d3a50;line-height:2;margin:0;">
        Model · mistral-small-2506<br>
        Embed · mistral-embed (384d)<br>
        Search · MMR (k=8)<br>
        Chunk · 1500 / 400 overlap<br>
        Store · Chroma DB
    </p>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  PAGE HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="ph-icon">📖</div>
    <div>
        <div class="ph-title">Lexis</div>
        <div class="ph-sub">Intelligent Multi-Document RAG System · Mistral AI</div>
    </div>
    <div class="ph-right">
        <div class="status-pill"><div class="pulse"></div>LIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  GATE: NO KB YET
# ─────────────────────────────────────────────────────────────
if not st.session_state.kb_ready:
    st.markdown("""
    <div class="welcome">
        <span class="wi">📚</span>
        <h3>Welcome to Lexis</h3>
        <p>Your intelligent reading companion powered by AI.</p>
        <p>Start by uploading PDF documents in the <strong>sidebar</strong> to build your knowledge base.</p>
        <div class="hint-row">
            <span class="hint">📖 Multi-document support</span>
            <span class="hint">🔍 Semantic search</span>
            <span class="hint">💬 Conversational AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────
#  LOAD RESOURCES
# ─────────────────────────────────────────────────────────────
try:
    embeddings = get_embeddings()
    llm = get_llm()
    vectorstore = get_vectorstore(embeddings)

    if vectorstore is None:
        st.warning("⚠️ Knowledge base folder missing. Please rebuild from the sidebar.")
        st.stop()

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": CONFIG["retriever_k"],
            "fetch_k": CONFIG["retriever_fetch_k"],
            "lambda_mult": CONFIG["retriever_lambda"]
        },
    )
    logger.info("✅ All resources loaded successfully")

except Exception as e:
    logger.error(f"Failed to load resources: {e}")
    st.error(f"❌ Failed to load resources: {str(e)}")
    st.stop()

# ─────────────────────────────────────────────────────────────
#  DOCUMENT FILTER
# ─────────────────────────────────────────────────────────────
try:
    raw_meta = vectorstore.get()["metadatas"]
    all_sources = sorted({m.get("source", "Unknown") for m in raw_meta if m})

    col_fil, col_info = st.columns([3, 2])
    with col_fil:
        selected_doc = st.selectbox(
            "🔖 Filter by document",
            ["All Documents"] + all_sources,
            label_visibility="collapsed"
        )
    with col_info:
        st.markdown(f"""
        <div style="text-align:right;padding-top:8px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
            color:var(--ivory-dim);">{len(all_sources)} document(s)</span>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    logger.error(f"Error getting document sources: {e}")
    st.warning("⚠️ Error loading document list")
    selected_doc = "All Documents"

# ─────────────────────────────────────────────────────────────
#  PROMPT TEMPLATE - ENHANCED
# ─────────────────────────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Lexis, an advanced literary AI assistant with deep knowledge across multiple documents.

Your responsibilities:
- Answer questions using ONLY the provided document context
- Synthesize information across multiple passages and documents when relevant
- Be accurate, clear, well-structured, and engaging
- If information isn't in the context, say so honestly - never fabricate or hallucinate
- Reference specific documents and pages to strengthen answers
- Use proper formatting: paragraphs, lists, emphasis where appropriate
- Maintain a professional yet conversational tone
- For complex questions, break answers into logical sections
- Highlight key insights and connections between ideas

Quality standards:
- Accuracy over length
- Cite sources naturally
- Acknowledge limitations in the source material
- Provide actionable insights when possible"""),

    ("human", """Context from documents:
{context}

Recent conversation:
{chat_history}

User question:
{question}

Please provide a comprehensive, well-structured answer based on the document context."""),
])

# ─────────────────────────────────────────────────────────────
#  LOAD AND DISPLAY CHAT HISTORY
# ─────────────────────────────────────────────────────────────
if not st.session_state.chat_history:
    st.session_state.chat_history = load_chat_history()

if not st.session_state.chat_history:
    st.markdown("""
    <div class="welcome">
        <span class="wi">🔍</span>
        <h3>Ask Anything About Your Books</h3>
        <p>Your knowledge base is ready. Start a conversation by typing a question below.</p>
        <div class="hint-row">
            <span class="hint">📖 Summarize content</span>
            <span class="hint">🔍 Find key concepts</span>
            <span class="hint">💡 Compare ideas</span>
            <span class="hint">🗂️ Extract themes</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        role = msg["role"]
        text = safe_text(msg["content"])
        ts = msg.get("time", "")
        
        if role == "user":
            st.markdown(f"""
            <div class="msg-row user">
                <div class="bubble user">{text}<span class="ts">{ts}</span></div>
                <div class="av av-user">👤</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row bot">
                <div class="av av-bot">📖</div>
                <div class="bubble bot">{text}<span class="ts">{ts}</span></div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  CHAT INPUT & PROCESSING
# ─────────────────────────────────────────────────────────────
query = st.chat_input("Ask anything about your documents…", key="chat_input")

if query:
    try:
        # 1. Show user message
        ts = ts_now()
        st.session_state.chat_history.append(
            {"role": "user", "content": query, "time": ts}
        )

        st.markdown(f"""
        <div class="chat-wrap">
            <div class="msg-row user">
                <div class="bubble user">
                    {safe_text(query)}<span class="ts">{ts}</span>
                </div>
                <div class="av av-user">👤</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # 2. Build conversation history
        history_text = "\n".join(
            f"{m['role'].capitalize()}: {m['content'][:500]}"  # Limit to 500 chars per message
            for m in st.session_state.chat_history[:-1][-4:]  # Last 4 turns
        )

        # 3. ENHANCED: Multi-step query rewriting
        with st.spinner("🔎 Analyzing your question…"):
            try:
                # First attempt: Standard rewriting
                rewrite_prompt = (
                    "Rewrite the following question to be clear, specific, and optimal for semantic document retrieval. "
                    "Include context from previous conversation if relevant. Output ONLY the rewritten question.\n\n"
                    f"Previous context:\n{history_text}\n\n"
                    f"Original question: {query}"
                )
                rewritten = llm.invoke(rewrite_prompt).content.strip()
                
                # Validation: if rewritten is too short or seems malformed, use original
                if len(rewritten.split()) < 2:
                    rewritten = query
                    
            except Exception as e:
                logger.warning(f"Query rewriting failed, using original: {e}")
                rewritten = query

        # 4. ENHANCED: Retrieve with filtering
        with st.spinner("📚 Searching knowledge base…"):
            try:
                # Get raw results
                docs = retriever.invoke(rewritten)
                
                # Apply source filter
                if selected_doc != "All Documents":
                    docs = [d for d in docs if d.metadata.get("source") == selected_doc]
                    
                    if not docs:
                        # Fallback: search all documents if none match filter
                        docs = retriever.invoke(rewritten)
                
                # Re-rank using semantic scoring
                query_words = set(rewritten.lower().split())
                docs_scored = [
                    (d, semantic_score_doc(d, query_words, rewritten))
                    for d in docs
                ]
                docs_scored.sort(key=lambda x: x[1], reverse=True)
                docs = [d for d, _ in docs_scored[:6]]  # Keep top 6
                
                logger.info(f"Retrieved {len(docs)} documents for query")

            except Exception as e:
                logger.error(f"Retrieval error: {e}")
                st.error(f"❌ Error searching knowledge base: {str(e)}")
                st.session_state.chat_history.pop()
                st.stop()

        if not docs:
            st.warning(
                "⚠️ No relevant passages found. Try rephrasing or switch to **All Documents**."
            )
            st.session_state.chat_history.pop()
            st.stop()

        # 5. Format context with structure
        context, overlap_percent = format_context_with_structure(docs)

        # 6. Generate answer with streaming
        final_prompt = prompt.invoke({
            "context": context,
            "question": query,
            "chat_history": history_text,
        })

        st.markdown('<div class="sec-head"><span class="sec-head-icon">💬</span>Answer</div>', unsafe_allow_html=True)
        
        placeholder = st.empty()
        full_text = ""
        _last_render = 0

        try:
            for chunk in llm.stream(final_prompt):
                full_text += chunk.content
                if len(full_text) - _last_render >= 20:
                    _last_render = len(full_text)
                    placeholder.markdown(
                        f'<div class="bubble bot" style="max-width:100%;">'
                        f'{safe_text(full_text)}<span style="opacity:0.35;">▌</span></div>',
                        unsafe_allow_html=True,
                    )

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            st.error(f"❌ Error during response generation")
            st.session_state.chat_history.pop()
            st.stop()

        # Final answer
        final_answer = full_text.strip()
        placeholder.markdown(
            f'<div class="bubble bot" style="max-width:100%;">{safe_text(final_answer)}</div>',
            unsafe_allow_html=True,
        )

        # 7. Save to history
        st.session_state.chat_history.append(
            {"role": "assistant", "content": final_answer, "time": ts_now()}
        )
        save_chat_history()

        # 8. Calculate & display confidence
        confidence = improved_confidence_score(docs, rewritten, overlap_percent)
        
        if confidence >= 75:
            fill = "linear-gradient(90deg, #2d8a52, #52c97a)"
            vc = "#52c97a"
            conf_text = "Excellent"
        elif confidence >= 50:
            fill = "linear-gradient(90deg, #a06010, #f0a847)"
            vc = "#f0a847"
            conf_text = "Good"
        else:
            fill = "linear-gradient(90deg, #8a2030, #e05a6a)"
            vc = "#e05a6a"
            conf_text = "Moderate"

        st.markdown(f"""
        <div class="conf-wrap">
            <div class="conf-lbl">Answer Quality</div>
            <div class="conf-track">
                <div class="conf-fill" style="width:{confidence}%;background:{fill};
                    box-shadow:0 0 10px {vc}66;"></div>
            </div>
            <div class="conf-val" style="color:{vc};">{confidence}% • {conf_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # 9. Expandable sources section
        st.markdown(f'<div class="sec-head"><span class="sec-head-icon">📚</span>Sources Used ({len(docs)})</div>', unsafe_allow_html=True)
        
        if st.button("🔽 Show Source Details", key="sources_expand"):
            st.session_state.show_sources = not st.session_state.show_sources

        if st.session_state.show_sources:
            st.markdown('<div class="expand-content">', unsafe_allow_html=True)
            for i, doc in enumerate(docs, 1):
                src = safe_text(doc.metadata.get("source", "Unknown"))
                page = doc.metadata.get("page", "?")
                snippet = safe_snippet(doc.page_content, 280)
                
                st.markdown(f"""
                <div class="src-card">
                    <div class="src-name">📄 {src}</div>
                    <div class="src-meta">Page {page} • Relevance: High</div>
                    <div class="src-snip">"{snippet}…"</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Log analytics
        log_analytics(query, confidence, len(docs))

    except Exception as e:
        logger.error(f"Unexpected error in chat processing: {e}", exc_info=True)
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
            st.session_state.chat_history.pop()

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <span>Lexis · Mistral AI · ChromaDB · Production Ready</span>
</div>
""", unsafe_allow_html=True)

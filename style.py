# style.py : le design de Kura (format application de téléphone)
import base64
import html
import os
from datetime import date, datetime
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
.stApp :is(p, h1, h2, h3, h4, label, input, textarea, button, li, b, small) {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ---------- fond + cadre de téléphone ---------- */
.stApp { background: radial-gradient(circle at 20% 10%, #E4ECFF 0%, #D3DEF4 60%, #C5D3EE 100%); }
header[data-testid="stHeader"] { background: transparent; }
.block-container {
    max-width: 420px !important;
    padding: 3rem 1.2rem 7rem !important;
    background: linear-gradient(180deg, #EEF4FF 0%, #F8FAFF 100%);
    position: relative;
    overflow: clip;              /* coupe les bulles décoratives sans bloquer le défilement */
    flex-shrink: 0 !important;   /* le téléphone grandit avec le contenu */
    height: auto !important;
}
@media (min-width: 640px) {
    .block-container {
        margin: 28px auto !important;
        min-height: 860px;
        border-radius: 46px;
        box-shadow: 0 0 0 10px #0F172A, 0 30px 70px rgba(15, 23, 42, .35);
    }
    .block-container::before {
        content: ""; position: absolute; top: 12px; left: 50%;
        transform: translateX(-50%); width: 110px; height: 28px;
        background: #0F172A; border-radius: 20px; z-index: 5;
    }
}

/* ---------- login ---------- */
.kura-blob { position: absolute; border-radius: 50%; pointer-events: none; z-index: 0; opacity: .55;
             background: radial-gradient(circle at 30% 30%, #FFFFFF 0%, #C7D7FF 55%, #8FB0FF 100%); }
.kura-blob.b1 { width: 220px; height: 220px; top: -90px; left: -90px; }
.kura-blob.b2 { width: 120px; height: 120px; top: 260px; right: -60px; }
.kura-blob.b3 { width: 200px; height: 200px; top: 620px; right: -80px; }
.kura-logo { position: relative; z-index: 1; width: 128px; height: 128px; margin: 48px auto 24px;
             border-radius: 36px; display: flex; align-items: center; justify-content: center;
             font-size: 62px; background: rgba(255, 255, 255, .55); backdrop-filter: blur(10px);
             box-shadow: inset 0 0 0 1.5px rgba(255, 255, 255, .9), 0 20px 40px rgba(37, 99, 235, .18); }
.kura-welcome { text-align: center; font-size: 2.3rem; font-weight: 800; color: #0B1437; letter-spacing: -.02em; }
.kura-sub { text-align: center; color: #475569; letter-spacing: .3em; font-size: .78rem; margin: 6px 0 26px; }
.kura-divider { display: flex; align-items: center; gap: 12px; color: #64748B;
                font-size: .72rem; letter-spacing: .25em; margin: 22px 0 10px; }
.kura-divider::before, .kura-divider::after { content: ""; flex: 1; height: 1px; background: #C7D2FE; }

/* ---------- champs et boutons ---------- */
[data-testid="stForm"] { border: none; padding: 0; }
.stTextInput [data-baseweb="input"] {
    background: rgba(255, 255, 255, .6) !important;
    border: 1px solid rgba(255, 255, 255, .95) !important;
    border-radius: 20px !important;
    box-shadow: inset 0 1px 0 #FFFFFF, 0 10px 24px rgba(37, 99, 235, .10) !important;
    backdrop-filter: blur(8px); }
.stTextInput [data-baseweb="input"]:focus-within { border-color: #93B4FF !important; }
.stTextInput [data-baseweb="input"] > div,
.stTextInput [data-baseweb="input"] input { background: transparent !important; border: none !important; }
.stTextInput input { padding: 16px 18px !important; color: #0F172A !important; }

/* ---------- login : icônes dans les champs ---------- */
.st-key-login_user [data-baseweb="input"] {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='1.8' stroke-linecap='round'%3E%3Ccircle cx='12' cy='8' r='4'/%3E%3Cpath d='M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important; background-position: 20px center !important; }
.st-key-login_pass [data-baseweb="input"] {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='1.8' stroke-linecap='round'%3E%3Crect x='5' y='10' width='14' height='10' rx='2.5'/%3E%3Cpath d='M8 10V7a4 4 0 0 1 8 0v3'/%3E%3Ccircle cx='12' cy='15' r='1.2'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important; background-position: 20px center !important; }
.st-key-login_user input, .st-key-login_pass input { padding: 20px 16px 20px 58px !important; }
.st-key-login_pass button { background: transparent !important; margin-right: 10px; }

/* Remember me + Forgot password sur une ligne */
.st-key-loginrow [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; align-items: center !important; }
.st-key-loginrow [data-testid="stColumn"] { min-width: 0 !important; width: auto !important; flex: 1 1 0 !important; }
.st-key-loginrow .stCheckbox { background: transparent !important; box-shadow: none !important;
                               padding: 0 !important; margin: 0 !important; }
.st-key-loginrow [data-testid="stMarkdownContainer"] p { margin: 0 !important; }
.kura-forgot { text-align: right; color: #1D4ED8; font-weight: 600; font-size: .92rem; margin: 0; }

/* Gros bouton Login pleine largeur avec la flèche dans un rond */
.st-key-loginbtn [data-testid="stFormSubmitButton"],
.st-key-loginbtn [data-testid="stFormSubmitButton"] > *,
.st-key-loginbtn button { width: 100% !important; }
.st-key-loginbtn button { position: relative; min-height: 62px; padding: 0 60px !important;
    background: linear-gradient(90deg, #3B82F6 0%, #2563EB 50%, #1D4ED8 100%) !important;
    box-shadow: 0 16px 34px rgba(37, 99, 235, .40), inset 0 1px 0 rgba(255, 255, 255, .35) !important; }
.st-key-loginbtn button p { font-size: 1.2rem !important; font-weight: 700 !important; }
.st-key-loginbtn button::after {
    content: "→"; position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    width: 42px; height: 42px; border-radius: 50%; background: rgba(255, 255, 255, .22);
    color: white; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }

/* 3 boutons ronds en verre */
.st-key-social [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important;
                                                   justify-content: center !important; gap: 20px !important; }
.st-key-social [data-testid="stColumn"] { flex: 0 0 70px !important; width: 70px !important; min-width: 0 !important; }
.st-key-social [data-testid="stButton"],
.st-key-social [data-testid="stButton"] > *,
.st-key-social button { width: 70px !important; }
.st-key-social button { height: 66px !important; padding: 0 !important; border-radius: 20px !important;
    background: rgba(255, 255, 255, .65) !important;
    box-shadow: inset 0 1px 0 #FFFFFF, inset 0 0 0 1px rgba(255, 255, 255, .9),
                0 12px 24px rgba(37, 99, 235, .14) !important; }
.st-key-social button p { font-size: 1.7rem !important; font-weight: 800 !important; }
.st-key-social [data-testid="stColumn"]:nth-child(1) button p { color: #EA4335 !important; }
.st-key-social [data-testid="stColumn"]:nth-child(2) button p { color: #0F172A !important; }
.st-key-social [data-testid="stColumn"]:nth-child(3) button p { color: #1877F2 !important; }
.kura-tagline { text-align: center; letter-spacing: .3em; font-size: .7rem; color: #475569; margin: 26px 0 14px; }
[class*="kura-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stButton button, .stFormSubmitButton button {
    width: 100%; border: none !important; border-radius: 999px !important;
    background: linear-gradient(90deg, #3B82F6, #1D4ED8) !important;
    padding: .75rem 1.2rem !important; box-shadow: 0 10px 22px rgba(37, 99, 235, .28); }
.stButton button p, .stFormSubmitButton button p { color: white !important; font-weight: 600; }
.stButton button:hover, .stFormSubmitButton button:hover { filter: brightness(1.08); }

/* ---------- accueil ---------- */
.kura-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.kura-initial { width: 42px; height: 42px; border-radius: 50%; color: white; font-weight: 700;
                background: linear-gradient(135deg, #3B82F6, #1D4ED8);
                display: flex; align-items: center; justify-content: center; }
.kura-bell { position: relative; width: 42px; height: 42px; border-radius: 50%; background: white;
             display: flex; align-items: center; justify-content: center;
             box-shadow: 0 4px 12px rgba(15, 23, 42, .08); }
.kura-dot { position: absolute; top: 9px; right: 10px; width: 8px; height: 8px;
            border-radius: 50%; background: #EF4444; }
.kura-hello { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.kura-doc { width: 96px; height: 96px; flex-shrink: 0; border-radius: 50%; font-size: 54px;
            display: flex; align-items: center; justify-content: center;
            background: radial-gradient(circle, #DBEAFE 0%, #BFDBFE 100%); }
.kura-greeting { color: #64748B; font-size: 1rem; margin: 0; }
.kura-title { font-size: 2rem; font-weight: 800; line-height: 1.15; color: #0F172A; margin: 2px 0 16px; }
.kura-title span { color: #2563EB; }

.kura-hero { display: flex; justify-content: space-between; align-items: center;
             background: linear-gradient(135deg, #3B82F6, #1D4ED8); border-radius: 24px;
             padding: 20px 22px; margin: 8px 0 18px; box-shadow: 0 12px 28px rgba(37, 99, 235, .3); }
.kura-hero-title { color: white; font-size: 1.25rem; font-weight: 700; }
.kura-hero-text { color: #DBEAFE; font-size: .9rem; margin-top: 4px; }
.kura-hero-pill { display: inline-block; margin-top: 12px; background: white; color: #1D4ED8;
                  font-weight: 600; font-size: .85rem; border-radius: 12px; padding: 7px 14px; }
.kura-hero-icon { font-size: 64px; filter: drop-shadow(0 8px 12px rgba(0, 0, 0, .2)); }

.kura-section { font-weight: 700; color: #0F172A; font-size: 1.1rem; margin: 18px 0 8px; }
.kura-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.kura-tile { background: white; border-radius: 18px; padding: 12px 4px; text-align: center;
             box-shadow: 0 4px 14px rgba(15, 23, 42, .06); }
.kura-tile-icon { width: 40px; height: 40px; margin: 0 auto 6px; border-radius: 50%; font-size: 20px;
                  background: #EAF1FF; display: flex; align-items: center; justify-content: center; }
.kura-tile b { display: block; font-size: .75rem; color: #0F172A; }
.kura-tile small { display: block; font-size: .62rem; color: #64748B; }

.kura-card { background: white; border-radius: 20px; padding: 16px; margin: 12px 0 8px;
             display: flex; gap: 14px; align-items: center; box-shadow: 0 4px 14px rgba(15, 23, 42, .07); }
.kura-avatar { width: 52px; height: 52px; border-radius: 50%; flex-shrink: 0; font-size: 26px;
               background: #DBEAFE; display: flex; align-items: center; justify-content: center; }
.kura-name { font-weight: 700; color: #0F172A; }
.kura-meta { color: #64748B; font-size: .85rem; }
.kura-badge { margin-left: auto; align-self: flex-start; background: #2563EB; color: white;
              border-radius: 999px; padding: 3px 12px; font-size: .72rem; }

.kura-tip { display: flex; justify-content: space-between; align-items: center; background: white;
            border-radius: 20px; padding: 16px 18px; margin: 18px 0; box-shadow: 0 4px 14px rgba(15, 23, 42, .06); }
.kura-tip small { color: #2563EB; font-weight: 600; display: block; margin-bottom: 4px; }
.kura-tip b { color: #0F172A; font-size: .95rem; }
.kura-tip-icon { font-size: 40px; }

.stCheckbox { background: white; border-radius: 16px; padding: 12px 14px; margin-bottom: 6px;
              box-shadow: 0 4px 14px rgba(15, 23, 42, .06); }
[data-testid="stExpander"] { background: white; border: none; border-radius: 16px;
                             box-shadow: 0 2px 8px rgba(15, 23, 42, .05); }
[data-testid="stChatMessage"] { background: white; border-radius: 18px;
                                box-shadow: 0 4px 14px rgba(15, 23, 42, .06); }

/* ---------- barre de navigation en bas ---------- */
.stTabs [data-baseweb="tab-list"] {
    position: fixed; bottom: 34px; left: 50%; transform: translateX(-50%);
    width: 372px; max-width: calc(100% - 24px); z-index: 999;
    justify-content: space-around; padding: 8px; border-radius: 24px;
    background: rgba(255, 255, 255, .92); backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(15, 23, 42, .15); }
.stTabs [data-baseweb="tab"] { height: auto; padding: 8px 10px; border-radius: 16px; }
.stTabs [data-baseweb="tab"] p { font-size: .78rem; color: #64748B; }
.stTabs [aria-selected="true"] { background: #EAF1FF; }
.stTabs [aria-selected="true"] p { color: #2563EB; font-weight: 700; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- boutons interactifs (services, bannière, retour, navigation) ---------- */
.st-key-services [data-testid="stHorizontalBlock"],
.st-key-nav [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 6px !important; }
.st-key-services [data-testid="stColumn"],
.st-key-nav [data-testid="stColumn"] { min-width: 0 !important; width: auto !important; flex: 1 1 0 !important; }

/* services : icône seule ; au survol / appui -> pilule bleue avec le nom (comme la barre du bas) */
.st-key-services [data-testid="stColumn"] { transition: flex .25s ease; }
.st-key-services [data-testid="stColumn"]:has(button:hover),
.st-key-services [data-testid="stColumn"]:has(button:active) { flex: 2.2 1 0 !important; }
.st-key-services [data-testid="stColumn"] > *,
.st-key-services [data-testid="stVerticalBlock"],
.st-key-services [data-testid="stElementContainer"],
.st-key-services [data-testid="stButton"],
.st-key-services .stButton,
.st-key-services .stButton > *,
.st-key-services .stButton button { width: 100% !important; max-width: none !important; }
.st-key-services .stButton button {
    height: 58px; min-width: 0; padding: 0 10px !important; border-radius: 16px !important;
    background: #FFFFFF !important; box-shadow: 0 4px 14px rgba(15, 23, 42, .06) !important;
    transition: background .2s ease, box-shadow .2s ease; }
.st-key-services .stButton button div { gap: 0 !important; }
.st-key-services .stButton button [data-testid="stIconMaterial"] {
    margin: 0 !important; color: #2563EB; font-size: 1.6rem; transition: color .2s ease; }
.st-key-services .stButton button [data-testid="stMarkdownContainer"] {
    max-width: 0; opacity: 0; overflow: hidden; margin: 0;
    transition: max-width .25s ease, opacity .2s ease, margin .25s ease; }
.st-key-services .stButton button p {
    color: #FFFFFF !important; font-size: .82rem; font-weight: 600; margin: 0; white-space: nowrap; }
.st-key-services .stButton button:hover,
.st-key-services .stButton button:active {
    background: #2563EB !important; box-shadow: 0 8px 18px rgba(37, 99, 235, .35) !important; }
.st-key-services .stButton button:hover [data-testid="stIconMaterial"],
.st-key-services .stButton button:active [data-testid="stIconMaterial"] { color: #FFFFFF; }
.st-key-services .stButton button:hover [data-testid="stMarkdownContainer"],
.st-key-services .stButton button:active [data-testid="stMarkdownContainer"] {
    max-width: 110px; opacity: 1; margin-left: 6px; }

.st-key-hero { position: relative; background: linear-gradient(135deg, #3B82F6, #1D4ED8);
               border-radius: 24px; padding: 20px 22px; margin: 8px 0 6px;
               box-shadow: 0 12px 28px rgba(37, 99, 235, .3); }
.st-key-hero::after { content: "🗓️"; position: absolute; right: 22px; top: 50%;
                      transform: translateY(-50%); font-size: 64px; pointer-events: none;
                      filter: drop-shadow(0 8px 12px rgba(0, 0, 0, .2)); }
.st-key-hero .kura-hero-text { max-width: 68%; }
.st-key-hero .stButton button { width: auto !important; background: white !important;
                                box-shadow: none !important; padding: .45rem 1.1rem !important;
                                border-radius: 12px !important; }
.st-key-hero .stButton button p { color: #1D4ED8 !important; }

.st-key-back .stButton button { width: auto !important; background: white !important;
                                padding: .4rem 1rem !important;
                                box-shadow: 0 4px 12px rgba(15, 23, 42, .08) !important; }
.st-key-back .stButton button p { color: #0F172A !important; }

.st-key-nav { position: fixed; bottom: 34px; left: 50%; transform: translateX(-50%);
              width: 372px; max-width: calc(100% - 24px); z-index: 999; padding: 8px 10px;
              border-radius: 28px; background: #FFFFFF;
              box-shadow: 0 10px 30px rgba(15, 23, 42, .15); }
.st-key-nav [data-testid="stHorizontalBlock"] { align-items: center; }
.st-key-nav [data-testid="stColumn"] { flex: 1 1 0 !important; transition: flex .25s ease; }
/* la colonne de l'onglet actif est plus large, pour la pilule icône + texte */
.st-key-nav [data-testid="stColumn"]:has([data-testid="stBaseButton-primary"]) { flex: 2.3 1 0 !important; }
.st-key-nav .stButton button { background: transparent !important; box-shadow: none !important;
                               min-height: 44px; padding: 8px 0 !important; border-radius: 999px !important; }
.st-key-nav .stButton button [data-testid="stIconMaterial"] { color: #475569; font-size: 1.45rem; }
.st-key-nav .stButton button p { font-size: .85rem; font-weight: 600; margin: 0; }
/* onglets inactifs : seulement l'icône */
.st-key-nav [data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] { display: none; }
/* onglet actif : pilule bleue avec icône + texte en blanc */
.st-key-nav .stButton [data-testid="stBaseButton-primary"] {
    background: #2563EB !important; padding: 8px 14px !important;
    box-shadow: 0 6px 14px rgba(37, 99, 235, .35) !important; }
.st-key-nav [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"],
.st-key-nav [data-testid="stBaseButton-primary"] p { color: #FFFFFF !important; }

/* ---------- proche aidant ---------- */
.kura-patient { display: flex; align-items: center; gap: 14px; border-radius: 22px; padding: 18px 20px;
                margin: 6px 0 18px; background: linear-gradient(135deg, #3B82F6, #1D4ED8);
                box-shadow: 0 10px 25px rgba(37, 99, 235, .25); }
.kura-patient .kura-avatar { background: rgba(255, 255, 255, .2); }
.kura-patient-name { color: white; font-size: 1.3rem; font-weight: 700; }
.kura-patient-sub { color: #DBEAFE; font-size: .9rem; }
.kura-alert { border-radius: 16px; padding: 14px 16px; margin-bottom: 8px;
              display: flex; gap: 10px; align-items: center; font-size: .95rem; }
.kura-alert.danger { background: #FEE2E2; color: #991B1B; }
.kura-alert.ok { background: #DCFCE7; color: #166534; }
.kura-row { background: white; border-radius: 16px; padding: 12px 16px; margin-bottom: 8px;
            display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 14px rgba(15, 23, 42, .06); }
.kura-pill { margin-left: auto; border-radius: 999px; padding: 3px 12px; font-size: .75rem; font-weight: 600; }
.kura-pill.taken { background: #DCFCE7; color: #166534; }
.kura-pill.pending { background: #F1F5F9; color: #475569; }
.kura-pill.missed { background: #FEE2E2; color: #991B1B; }

/* ================= LOGIN (copie de la maquette) ================= */
.kl-wrap { position: relative; overflow: hidden; text-align: center;
           margin: -3rem -1.2rem 0; padding: 2.4rem 1.6rem 2rem; min-height: 820px;
           font-family: 'Plus Jakarta Sans', sans-serif; }
.kl-wrap * { font-family: 'Plus Jakarta Sans', sans-serif; box-sizing: border-box; }
.kl-blob { position: absolute; border-radius: 50%; pointer-events: none; }
.kl-b1 { width: 300px; height: 300px; top: -150px; left: -150px;
         background: radial-gradient(circle at 60% 60%, #EEF2FF 0%, #DCE5FB 100%);
         box-shadow: 14px 14px 0 rgba(110, 150, 255, .35); }
.kl-b2 { width: 150px; height: 150px; top: 290px; right: -78px;
         background: radial-gradient(circle at 30% 30%, #F5F8FF 0%, #BFD0FF 100%);
         box-shadow: 0 12px 30px rgba(59, 130, 246, .20); }
.kl-b3 { width: 260px; height: 260px; bottom: -170px; left: -120px;
         background: radial-gradient(circle at 40% 30%, #EEF2FF 0%, #D6E0FA 100%);
         box-shadow: 0 -12px 0 rgba(110, 150, 255, .35); }
.kl-b4 { width: 360px; height: 360px; bottom: -230px; right: -200px;
         background: radial-gradient(circle at 30% 30%, #F1F5FF 0%, #DCE5FB 100%);
         box-shadow: -14px -10px 0 rgba(255, 255, 255, .9), -20px -16px 0 rgba(110, 150, 255, .25); }

.kl-moon { position: absolute; top: 4px; right: 6px; width: 54px; height: 54px; border-radius: 16px;
           display: flex; align-items: center; justify-content: center; z-index: 2;
           background: rgba(255, 255, 255, .6);
           box-shadow: inset 0 1px 0 #fff, 0 10px 22px rgba(37, 99, 235, .12); }
.kl-logo { position: relative; z-index: 1; width: 160px; height: 160px; margin: 46px auto 28px;
           border-radius: 46px; display: flex; align-items: center; justify-content: center;
           background: linear-gradient(145deg, rgba(255, 255, 255, .85), rgba(226, 235, 255, .55));
           box-shadow: inset 0 2px 0 #fff, inset 0 -8px 18px rgba(37, 99, 235, .08),
                       0 0 0 1px rgba(255, 255, 255, .9), 0 26px 50px rgba(37, 99, 235, .18); }
.kl-logo::before { content: ""; position: absolute; width: 120px; height: 120px; border-radius: 50%;
                   background: radial-gradient(circle, rgba(59, 130, 246, .35) 0%, rgba(59, 130, 246, 0) 70%);
                   animation: kl-glow 1.2s ease-in-out infinite; }
.kl-heart { position: relative; filter: drop-shadow(0 12px 16px rgba(29, 78, 216, .35)); }
.kl-beat-g { transform-box: fill-box; transform-origin: center;
             animation: kl-beat 1.2s ease-in-out infinite; }
.kl-heart-img { animation: kl-pulse 1.2s ease-in-out infinite; }
@keyframes kl-pulse { 0%, 100% { transform: scale(1); } 14% { transform: scale(1.05); }
                      28% { transform: scale(.99); } 42% { transform: scale(1.03); } 70% { transform: scale(1); } }
.kl-ecg { stroke-dasharray: 150; stroke-dashoffset: 150; animation: kl-ecg 1.2s linear infinite; }
/* logo image (assets/heart.png) : carré arrondi dans le cadre en verre */
.kl-heart.kl-heart-img { width: 136px; height: 136px; object-fit: cover; border-radius: 36px;
    box-shadow: 0 14px 30px rgba(15, 40, 120, .35); filter: none; }
@keyframes kl-beat { 0%, 100% { transform: scale(1); } 14% { transform: scale(1.12); }
                     28% { transform: scale(.97); } 42% { transform: scale(1.07); } 70% { transform: scale(1); } }
@keyframes kl-glow { 0%, 100% { transform: scale(.85); opacity: .5; } 20% { transform: scale(1.15); opacity: 1; } }
@keyframes kl-ecg { 0% { stroke-dashoffset: 150; } 60% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: -150; } }
@media (prefers-reduced-motion: reduce) {
    .kl-beat-g, .kl-heart-img, .kl-ecg, .kl-logo::before { animation: none; stroke-dashoffset: 0; } }
.kl-title { position: relative; z-index: 1; font-size: 2.3rem; font-weight: 800;
            color: #0B1437; letter-spacing: -.02em; line-height: 1.1; }
.kl-sub { position: relative; z-index: 1; font-size: .85rem; color: #334155;
          letter-spacing: .38em; margin: 12px 0 30px; }

.kl-form { position: relative; z-index: 1; margin: 0; }
.kl-field { display: flex; align-items: center; gap: 18px; height: 64px; padding: 0 22px;
            margin: 0 0 16px; border-radius: 20px; cursor: text;
            background: rgba(255, 255, 255, .55);
            box-shadow: inset 0 1px 0 #fff, inset 0 0 0 1px rgba(255, 255, 255, .95),
                        0 10px 24px rgba(37, 99, 235, .10); }
.kl-field svg { flex-shrink: 0; }
.kl-field input { flex: 1; min-width: 0; border: none !important; outline: none !important;
                  background: transparent !important; box-shadow: none !important;
                  font-size: 1rem; color: #0F172A; padding: 0; height: 100%; }
.kl-field input::placeholder { color: #64748B; }
.kl-field:focus-within { box-shadow: inset 0 1px 0 #fff, inset 0 0 0 1.5px #93B4FF,
                                     0 10px 24px rgba(37, 99, 235, .16); }

.kl-row { display: flex; justify-content: space-between; align-items: center; margin: 4px 4px 22px; }
.kl-remember { display: flex; align-items: center; gap: 10px; font-size: .95rem; color: #0F172A; cursor: pointer; }
.kl-remember input { width: 24px; height: 24px; margin: 0; accent-color: #2563EB; cursor: pointer; }
.kl-forgot { color: #1D4ED8 !important; font-weight: 600; font-size: .95rem; text-decoration: none !important; }

.kl-login { position: relative; width: 100%; height: 62px; border: none; border-radius: 999px;
            cursor: pointer; color: #fff; font-size: 1.25rem; font-weight: 700;
            background: linear-gradient(90deg, #3B82F6 0%, #2563EB 55%, #1E40AF 100%);
            box-shadow: 0 18px 36px rgba(37, 99, 235, .40), inset 0 1px 0 rgba(255, 255, 255, .45),
                        inset 0 -3px 8px rgba(30, 64, 175, .35); }
.kl-login:hover { filter: brightness(1.07); }
.kl-arrow { position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
            width: 44px; height: 44px; border-radius: 50%; background: rgba(255, 255, 255, .18);
            display: flex; align-items: center; justify-content: center; }

.kl-divider { position: relative; z-index: 1; display: flex; align-items: center; gap: 22px;
              margin: 34px 22px 26px; font-size: .78rem; letter-spacing: .32em; color: #334155; }
.kl-divider::before, .kl-divider::after { content: ""; flex: 1; height: 1.5px; background: #9DB0D8; }
.kl-social { position: relative; z-index: 1; display: flex; justify-content: center; gap: 22px; }
.kl-social button { width: 72px; height: 68px; border: none; border-radius: 22px; cursor: pointer;
                    font-size: 1.8rem; font-weight: 800; background: rgba(255, 255, 255, .6);
                    box-shadow: inset 0 1px 0 #fff, inset 0 0 0 1px rgba(255, 255, 255, .95),
                                0 12px 24px rgba(37, 99, 235, .14); }
.kl-g { color: #EA4335; } .kl-a { color: #0F172A; } .kl-f { color: #1877F2; }
.kl-tagline { position: relative; z-index: 1; margin-top: 40px; font-size: .74rem;
              letter-spacing: .34em; color: #334155; }
.kl-corner { position: absolute; right: 14px; bottom: 34px; z-index: 1; text-align: left;
             font-size: .62rem; letter-spacing: .28em; line-height: 2; color: #334155; }
.kl-corner span { display: block; width: 22px; height: 2px; background: #334155; margin-top: 6px; }

/* ================= ASSISTANT IA : bulle flottante ================= */
.st-key-aifab { position: fixed !important; z-index: 1000; bottom: 118px;
                right: max(18px, calc(50% - 192px)); width: 62px !important; }
.st-key-aifab button {
    width: 62px !important; height: 62px !important; min-height: 0 !important; padding: 0 !important;
    border: none !important; border-radius: 50% !important; font-size: 0 !important;
    background: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2.2' stroke-linecap='round'%3E%3Cpath d='M4 10v4M8 7v10M12 4v16M16 7v10M20 10v4'/%3E%3C/svg%3E") center / 28px no-repeat,
                linear-gradient(135deg, #60A5FA, #1D4ED8) !important;
    animation: ka-pulse 2.4s ease-out infinite; }
.st-key-aifab button > * { visibility: hidden !important; }
@keyframes ka-pulse {
    0%   { box-shadow: 0 10px 24px rgba(37, 99, 235, .45), 0 0 0 0 rgba(59, 130, 246, .45); }
    70%  { box-shadow: 0 10px 24px rgba(37, 99, 235, .45), 0 0 0 16px rgba(59, 130, 246, 0); }
    100% { box-shadow: 0 10px 24px rgba(37, 99, 235, .45), 0 0 0 0 rgba(59, 130, 246, 0); } }
[data-testid="stPopoverBody"] { width: 340px !important; max-width: calc(100vw - 32px) !important;
                                border-radius: 24px !important; padding: 16px !important;
                                box-shadow: 0 24px 50px rgba(15, 23, 42, .25) !important; }
.ka-head { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.ka-head b { display: block; color: #0F172A; }
.ka-head small { color: #64748B; font-size: .75rem; }
.ka-dot { width: 38px; height: 38px; border-radius: 50%; color: #fff; font-size: 18px;
          display: flex; align-items: center; justify-content: center;
          background: linear-gradient(135deg, #60A5FA, #1D4ED8); }
.ka-msgs { max-height: 260px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; margin-bottom: 8px; }
.ka-b { padding: 10px 12px; border-radius: 16px; font-size: .9rem; line-height: 1.35; max-width: 85%; }
.ka-b.ai { align-self: flex-start; background: #EEF4FF; color: #0F172A; border-bottom-left-radius: 4px; }
.ka-b.me { align-self: flex-end; background: #2563EB; color: #fff; border-bottom-right-radius: 4px; }
</style>
"""

SERVICES = [
    ("🚗", "Rides", "Ask a friend"),
    ("💊", "Medication", "Daily reminders"),
    ("🤝", "Caregiver", "Share access"),
    ("💬", "Messages", "Your clinic"),
]

TIPS = [
    "Write down your questions before your appointment.",
    "Bring your medication list to every visit.",
    "Small steps count. You've got this 💙",
    "Ask someone you trust to come with you if you feel nervous.",
    "Keep your clinic's phone number somewhere easy to find.",
]


def load_css():
    st.markdown(CSS, unsafe_allow_html=True)


def _greeting():
    try:
        from zoneinfo import ZoneInfo
        hour = datetime.now(ZoneInfo("America/Toronto")).hour
    except Exception:
        hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


# ---------- login ----------
def login_header():
    st.markdown(
        '<div class="kura-blob b1"></div><div class="kura-blob b2"></div><div class="kura-blob b3"></div>'
        '<div class="kura-logo">💙</div>'
        '<div class="kura-welcome">Welcome Back</div>'
        '<div class="kura-sub">Sign in to continue</div>',
        unsafe_allow_html=True,
    )


# ---------- login (copie de la maquette, en HTML) ----------
_USER_SVG = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#475569" '
             'stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="8" r="4"/>'
             '<path d="M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>')
_LOCK_SVG = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#475569" '
             'stroke-width="1.8" stroke-linecap="round"><rect x="5" y="10" width="14" height="10" rx="2.5"/>'
             '<path d="M8 10V7a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15" r="1.2"/></svg>')
_EYE_SVG = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#475569" '
            'stroke-width="1.8" stroke-linecap="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/>'
            '<circle cx="12" cy="12" r="3"/><path d="M3 3l18 18"/></svg>')
_ARROW_SVG = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" '
              'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
_MOON_SVG = ('<svg width="24" height="24" viewBox="0 0 24 24"><path fill="#0B1437" '
             'd="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>')
_LOGO_SVG = ('<svg class="kl-heart" width="150" height="150" viewBox="0 0 120 120"><defs>'
             '<radialGradient id="kld" cx="35%" cy="30%" r="80%">'
             '<stop offset="0" stop-color="#F0F7FF" stop-opacity=".95"/>'
             '<stop offset=".55" stop-color="#93C5FD" stop-opacity=".75"/>'
             '<stop offset="1" stop-color="#2563EB" stop-opacity=".85"/></radialGradient>'
             '<radialGradient id="klhh" cx="35%" cy="30%" r="80%">'
             '<stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#93C5FD"/>'
             '<stop offset="1" stop-color="#2563EB"/></radialGradient>'
             '<filter id="klglow" x="-30%" y="-30%" width="160%" height="160%">'
             '<feGaussianBlur stdDeviation="2.6"/></filter></defs>'
             # épaisseur du disque (effet 3D)
             '<circle cx="61" cy="66" r="42" fill="#1D4ED8" opacity=".35"/>'
             # disque en verre
             '<circle cx="58" cy="62" r="42" fill="url(#kld)" stroke="#FFFFFF" stroke-width="3"/>'
             '<circle cx="58" cy="62" r="36.5" fill="none" stroke="#FFFFFF" stroke-opacity=".55" stroke-width="1.5"/>'
             '<path d="M27 46A36 36 0 0 1 52 27" fill="none" stroke="#FFFFFF" stroke-width="4" '
             'stroke-linecap="round" opacity=".9"/>'
             # ligne de battement lumineuse
             '<polyline points="24,64 41,64 47,52 53,80 61,36 69,74 74,64 92,64" fill="none" stroke="#3B82F6" '
             'stroke-width="9" stroke-linecap="round" stroke-linejoin="round" filter="url(#klglow)" opacity=".8"/>'
             '<polyline class="kl-ecg" points="24,64 41,64 47,52 53,80 61,36 69,74 74,64 92,64" fill="none" '
             'stroke="#FFFFFF" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>'
             # petit cœur en verre qui bat
             '<g class="kl-beat-g"><g transform="translate(76 14) scale(.34)">'
             '<path fill="url(#klhh)" stroke="#FFFFFF" stroke-width="7" d="M50 88C20 68 6 52 6 33'
             'C6 19 17 9 30 9C39 9 46 14 50 21C54 14 61 9 70 9C83 9 94 19 94 33C94 52 80 68 50 88Z"/>'
             '<ellipse cx="30" cy="28" rx="12" ry="7" fill="#FFFFFF" opacity=".75" transform="rotate(-32 30 28)"/>'
             '</g></g>'
             # étincelle
             '<path d="M30 30l1.6 4.4 4.4 1.6-4.4 1.6L30 42l-1.6-4.4L24 36l4.4-1.6z" fill="#FFFFFF"/>'
             '</svg>')

# Si une image 3D est dans assets/heart.png, on l'utilise comme logo (en bleu).
# Sinon, on garde le cœur dessiné en SVG.
_HEART_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "heart.png")


def _logo_html():
    if os.path.exists(_HEART_FILE):
        with open(_HEART_FILE, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (f'<img class="kl-heart kl-heart-img" src="data:image/png;base64,{b64}" '
                f'width="136" height="136" alt="Kura">')
    return _LOGO_SVG


def login_screen():
    """Écran de connexion. Le bouton Login recharge la page avec ?user=..."""
    st.markdown(
        '<div class="kl-wrap">'
        '<div class="kl-blob kl-b1"></div><div class="kl-blob kl-b2"></div>'
        '<div class="kl-blob kl-b3"></div><div class="kl-blob kl-b4"></div>'
        f'<div class="kl-moon">{_MOON_SVG}</div>'
        f'<div class="kl-logo">{_logo_html()}</div>'
        '<div class="kl-title">Welcome Back</div>'
        '<div class="kl-sub">Sign in to continue</div>'
        '<form class="kl-form" method="get" action="" target="_self">'
        f'<label class="kl-field">{_USER_SVG}'
        '<input name="user" type="text" placeholder="Username or Email" autocomplete="username" required></label>'
        f'<label class="kl-field">{_LOCK_SVG}'
        '<input type="password" placeholder="Password" autocomplete="current-password">'
        f'{_EYE_SVG}</label>'
        '<div class="kl-row"><label class="kl-remember"><input type="checkbox" checked>Remember Me</label>'
        '<a class="kl-forgot" href="#">Forgot Password?</a></div>'
        f'<button class="kl-login" type="submit">Login<span class="kl-arrow">{_ARROW_SVG}</span></button>'
        '</form>'
        '<div class="kl-divider">OR CONTINUE WITH</div>'
        '<div class="kl-social">'
        '<button type="button" class="kl-g" title="Demo only">G</button>'
        '<button type="button" class="kl-a" title="Demo only">🍎</button>'
        '<button type="button" class="kl-f" title="Demo only">f</button>'
        '</div>'
        '<div class="kl-tagline">CARE &nbsp;•&nbsp; CONNECT &nbsp;•&nbsp; GROW TOGETHER</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def divider(text):
    st.markdown(f'<div class="kura-divider">{text}</div>', unsafe_allow_html=True)


# ---------- accueil ----------
def home_header(name):
    initial = html.escape(name.strip()[:1].upper())
    name = html.escape(name)
    st.markdown(
        f'<div class="kura-top"><div class="kura-initial">{initial}</div>'
        f'<div class="kura-bell">🔔<span class="kura-dot"></span></div></div>'
        f'<div class="kura-hello"><div>'
        f'<p class="kura-greeting">{_greeting()}, {name} 👋</p>'
        f'<p class="kura-title">Take care of<br>your <span>health.</span></p>'
        f'</div><div class="kura-doc">👩‍⚕️</div></div>',
        unsafe_allow_html=True,
    )


def header(name):          # ancien nom, gardé pour compatibilité
    home_header(name)


def book_banner():
    st.markdown(
        '<div class="kura-hero"><div>'
        '<div class="kura-hero-title">Book Appointment</div>'
        '<div class="kura-hero-text">Consult with trusted doctors anytime.</div>'
        '<span class="kura-hero-pill">Open 📅 Book below</span>'
        '</div><div class="kura-hero-icon">🗓️</div></div>',
        unsafe_allow_html=True,
    )


def hero(title, text, icon="🗓️"):
    st.markdown(
        f'<div class="kura-hero"><div>'
        f'<div class="kura-hero-title">{title}</div>'
        f'<div class="kura-hero-text">{text}</div>'
        f'</div><div class="kura-hero-icon">{icon}</div></div>',
        unsafe_allow_html=True,
    )


def services_grid():
    tiles = "".join(
        f'<div class="kura-tile"><div class="kura-tile-icon">{icon}</div>'
        f'<b>{title}</b><small>{sub}</small></div>'
        for icon, title, sub in SERVICES
    )
    st.markdown(
        f'<div class="kura-section">Our services</div><div class="kura-grid">{tiles}</div>',
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="kura-section">{title}</div>', unsafe_allow_html=True)


def tip_card():
    tip = TIPS[date.today().toordinal() % len(TIPS)]
    st.markdown(
        f'<div class="kura-tip"><div><small>Daily tip</small><b>{tip}</b></div>'
        f'<div class="kura-tip-icon">💙</div></div>',
        unsafe_allow_html=True,
    )


def appointment_card(a):
    doctor = html.escape(a.get("doctor", "Your clinic"))
    title = html.escape(a["title"])
    st.markdown(
        f'<div class="kura-card"><div class="kura-avatar">🩺</div><div>'
        f'<div class="kura-name">{doctor}</div>'
        f'<div class="kura-meta">{title}</div>'
        f'<div class="kura-meta">📅 {a["date"]} &nbsp; 🕒 {a["time"]}</div>'
        f'</div><span class="kura-badge">Confirmed</span></div>',
        unsafe_allow_html=True,
    )


# ---------- proche aidant ----------
def caregiver_title():
    st.markdown(
        f'<div class="kura-top"><div class="kura-initial">🤝</div>'
        f'<div class="kura-bell">🔔<span class="kura-dot"></span></div></div>'
        f'<p class="kura-greeting">{_greeting()} 👋</p>'
        f'<p class="kura-title">Caring,<br><span>together.</span></p>',
        unsafe_allow_html=True,
    )


def patient_banner(name):
    name = html.escape(name)
    st.markdown(
        f'<div class="kura-patient"><div class="kura-avatar">🙂</div><div>'
        f'<div class="kura-patient-name">{name}</div>'
        f'<div class="kura-patient-sub">You\'re following {name}\'s care · live</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def alert_box(text, kind="danger"):
    icon = "⚠️" if kind == "danger" else "✅"
    st.markdown(
        f'<div class="kura-alert {kind}">{icon} {html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def reminder_row(r, status):
    icons = {"Taken": "✅", "Pending": "⏳", "Missed": "❌"}
    title = html.escape(r["title"])
    st.markdown(
        f'<div class="kura-row">'
        f'<div class="kura-avatar" style="width:40px;height:40px;font-size:20px">💊</div><div>'
        f'<div class="kura-name">{title}</div>'
        f'<div class="kura-meta">📅 {r["date"]} &nbsp; 🕒 {r["time"]}</div>'
        f'</div><span class="kura-pill {status.lower()}">{icons[status]} {status}</span></div>',
        unsafe_allow_html=True,
    )
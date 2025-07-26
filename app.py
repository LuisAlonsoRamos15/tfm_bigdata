# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 09:41:36 2025

@author: luisa
"""

# app.py

import streamlit as st
from scraper_ui import scraper_ui
from eda_ui import eda_ui
from chatbot_ui import chatbot_ui
from modelo_ui import modelo_ui
from proyeccion_ui import proyeccion_financiera_ui 

st.set_page_config(page_title="TFM - Análisis Financiero con IA", layout="wide")

# Menú de navegación lateral
st.sidebar.title("🔍 Menú de Navegación")
opcion = st.sidebar.radio("Selecciona una sección:", [
    "📥 Scraper",
    "📊 Análisis EDA",
    "🤖 Chatbot",
    "📈 Proyección",
    "📂 Modelo IA"
])

# Enrutamiento
if opcion == "📥 Scraper":
    scraper_ui()

elif opcion == "📊 Análisis EDA":
    eda_ui()

elif opcion == "🤖 Chatbot":
    chatbot_ui()

elif opcion == "📈 Proyección":
    proyeccion_financiera_ui()

elif opcion == "📂 Modelo IA":
    modelo_ui()

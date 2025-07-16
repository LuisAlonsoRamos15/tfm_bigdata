# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 09:24:11 2025

@author: luisa
"""

# chatbot_ui.py

import streamlit as st
import pandas as pd
from chatbot_financiero_plus import (
    extraer_tickers_y_anio,
    obtener_datos_empresas,
    generar_prompt_comparativo,
    conversar_con_gpt,
)

def chatbot_ui():
    st.title("🤖 Chatbot Financiero")
    st.markdown("Haz una pregunta como: `Compara Apple y Microsoft en 2023`")

    pregunta = st.text_input("Tu pregunta financiera")

    if st.button("Enviar"):
        if not pregunta.strip():
            st.warning("⚠️ Escribe una pregunta antes de continuar.")
            return

        with st.spinner("🔍 Analizando tu pregunta..."):
            tickers, anio = extraer_tickers_y_anio(pregunta)

        if not tickers or not anio:
            st.error("❌ No se pudieron detectar correctamente los tickers o el año.")
            return

        with st.spinner("📊 Buscando datos financieros..."):
            df = obtener_datos_empresas(tickers, anio)

        if df is None or df.empty:
            st.warning("❌ No se encontraron datos para las empresas solicitadas.")
            return

        st.subheader("📊 Datos encontrados")
        st.dataframe(df)

        with st.spinner("🧠 Generando análisis con GPT..."):
            prompt = generar_prompt_comparativo(pregunta, df, anio)
            respuesta = conversar_con_gpt(prompt)

        st.subheader("💬 Respuesta del asistente")
        st.text(respuesta)

if __name__ == "__main__":
    chatbot_ui()

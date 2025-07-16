# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 09:09:45 2025

@author: luisa
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import tempfile
from scraper_module import obtener_datos_financieros, guardar_en_excel

def scraper_ui():
    st.title("📥 Descarga de Datos Financieros")
    
    ticker = st.text_input("Ticker de empresa (ej. AAPL, TSLA)")
    fuente = st.selectbox("Fuente de datos", ["Alpha Vantage", "Yahoo Finance"])

    if st.button("Descargar datos"):
            if not ticker:
                st.warning("⚠️ Debes ingresar un ticker antes de continuar.")
            else:
                try:
                    with st.spinner("Descargando datos..."):
                        ingresos, balance, flujo = obtener_datos_financieros(ticker, fuente)
                        for df_temp in [ingresos, balance, flujo]:
                            if "date" in df_temp.columns:
                                df_temp.drop(columns=["date"], inplace=True)
                    st.success("✅ Datos descargados")
                    st.subheader("Vista previa: Estado de Ingresos")
                    st.dataframe(ingresos.reset_index(drop=True)) 
                    st.subheader("Vista previa: Balance General")
                    st.dataframe(balance.reset_index(drop=True))
                    st.subheader("Vista previa: Flujo de Caja")
                    st.dataframe(flujo.reset_index(drop=True))
        
        
                    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                        ruta_excel = tmp.name
                        guardar_en_excel(ticker, ingresos, balance, flujo, ruta_excel)
                        with open(ruta_excel, "rb") as f:
                            st.download_button(
                                label="📥 Descargar Excel",
                                data=f,
                                file_name=f"datos_financieros_{ticker}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    
if __name__ == "__main__":
    scraper_ui()

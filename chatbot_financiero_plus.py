# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 15:13:34 2025

@author: luisa
"""

# chatbot_comparador.py

import pandas as pd
import joblib
import os
import yfinance as yf
from dotenv import load_dotenv
from pathlib import Path
import json
from openai import OpenAI
import openai
import streamlit as st

# Configuración
openai.api_key = st.secrets["OPENAI_API_KEY"]


# Cargar modelo y dataset
modelo = joblib.load("modelo_clasificador.pkl")
label_encoder = joblib.load("label_encoder.pkl")
df_base = pd.read_csv("01_dataset_depurado.csv")

# -----------------------------
# Extraer múltiples tickers y año
# -----------------------------
def extraer_tickers_y_anio(texto_usuario):
    prompt = (
        "Eres un asistente que recibe una pregunta financiera sobre varias empresas y un año. "
        "Devuelve un JSON con dos claves: 'tickers': una lista con los tickers bursátiles detectados (ej: ['AAPL','TSLA']), "
        "y 'anio': un número de 4 dígitos del año referido. NO EXPLIQUES NADA, solo devuelve el JSON.\n\n"
        f"Ejemplo de pregunta: {texto_usuario}"
    )

    respuesta = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente financiero."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    try:
        datos = json.loads(respuesta.choices[0].message.content)
        tickers = [t.upper() for t in datos["tickers"]]
        anio = str(datos["anio"])
        return tickers, anio
    except Exception as e:
        print("⚠️ Error interpretando respuesta de GPT:", e)
        return [], None

# -----------------------------
# Obtener datos de múltiples empresas
# -----------------------------
def obtener_datos_empresas(tickers, anio):
    resultados = []

    for ticker in tickers:
        fila = df_base[(df_base['Ticker'] == ticker) & (df_base['Year'].astype(str) == anio)]
        if fila.empty:
            # Intentar extraer de yfinance si no está en el dataset
            try:
                yf_data = yf.Ticker(ticker)
                income = yf_data.financials.T
                balance = yf_data.balance_sheet.T
                cashflow = yf_data.cashflow.T

                df = income.join(balance, how="outer", lsuffix="_income", rsuffix="_balance")
                df = df.join(cashflow, how="outer")
                df["Ticker"] = ticker
                df.reset_index(inplace=True)
                df.rename(columns={"index": "Year"}, inplace=True)

                fila = df[df["Year"].astype(str).str.contains(anio)]
                if fila.empty:
                    fila = df.sort_values(by="Year", ascending=False).head(1)
            except:
                continue
        else:
            fila = fila.head(1)

        # Predecir clase
        datos_modelo = fila.select_dtypes(include="number")
        datos_modelo = datos_modelo.reindex(modelo.feature_names_in_, axis=1, fill_value=0)
        pred = modelo.predict(datos_modelo)[0]
        clase = label_encoder.inverse_transform([pred])[0]
        fila["Label"] = clase

        resultados.append(fila)

    if resultados:
        return pd.concat(resultados, ignore_index=True)
    else:
        return None

# -----------------------------
# Crear prompt para comparación
# -----------------------------
def generar_prompt_comparativo(texto_usuario, datos, anio):
    contexto = (
        "Eres un analista financiero experto. Tu tarea es comparar varias empresas en base a sus datos financieros para el año especificado.\n\n"
        "Instrucciones:\n"
        "1. Analiza y compara solo los datos proporcionados.\n"
        "2. Considera métricas como 'Revenue', 'Net Income', 'ROE' y la clasificación IA en 'Label'.\n"
        "3. Explica brevemente qué empresa tuvo mejor desempeño según los datos.\n"
        "4. No inventes datos ni hables de años diferentes.\n\n"
    )

    prompt = (
        f"{contexto}\n"
        f"Pregunta del usuario: {texto_usuario}\n"
        f"Año solicitado: {anio}\n\n"
        f"Datos financieros disponibles:\n{datos.to_string(index=False)}\n\n"
        "Escribe una comparación profesional entre las empresas listadas."
    )

    return prompt

# -----------------------------
# Enviar a GPT para análisis
# -----------------------------
def conversar_con_gpt(prompt):
    respuesta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en análisis financiero."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return respuesta.choices[0].message.content

# -----------------------------
# Interfaz de consola
# -----------------------------
if __name__ == "__main__":
    print("🤖 Comparador financiero de empresas")
    print("Escribe una pregunta como: 'Compara Tesla y Apple en 2022' o '¿Quién lo hizo mejor entre AAPL, MSFT y NVDA en 2023?'\n")

    while True:
        entrada = input("Tu pregunta (o 'salir'): ").strip()
        if entrada.lower() == "salir":
            break

        tickers, anio = extraer_tickers_y_anio(entrada)

        if tickers and anio:
            df = obtener_datos_empresas(tickers, anio)
            if df is not None and not df.empty:
                prompt = generar_prompt_comparativo(entrada, df, anio)
                respuesta = conversar_con_gpt(prompt)
                print("\n📊 Comparación del asistente:\n")
                print(respuesta)
                print("\n" + "-" * 60 + "\n")
            else:
                print("❌ No se encontraron datos para las empresas solicitadas.")
        else:
            print("❌ No se pudieron detectar correctamente los tickers o el año.")

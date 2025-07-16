# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 09:39:14 2025

@author: luisa
"""

# modelo_ui.py

import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

def modelo_ui():
    st.title("🧠 Clasificador Financiero de Empresas")

    st.markdown("""
    ### Estrategia del Clasificador
    
    Se ha entrenado un modelo de aprendizaje automático usando un **Random Forest Classifier** (`scikit-learn`) sobre un dataset depurado de características numéricas financieras.
    
    La clasificación se basa en la siguiente lógica de negocio aplicada como etiquetas objetivo (**target**):
    
    - 🟢 **Sólida**: Empresas con `Net Income ≥ 0` y `ROE ≥ 5%`
    - 🟡 **Estable**: Empresas con `Net Income ≥ 0` pero `ROE < 5%`
    - 🔴 **Riesgosa**: Empresas con `Net Income < 0`
    
    El modelo predice automáticamente estas etiquetas a partir de métricas históricas, y se utiliza en otras secciones de la app como el EDA y el Chatbot para contextualizar el rendimiento de las empresas.
    """)


    # Cargar modelo y encoder
    clf = joblib.load("modelo_clasificador.pkl")
    le = joblib.load("label_encoder.pkl")
    df = pd.read_csv("01_dataset_depurado.csv")

    # Generar datos
    X = df[clf.feature_names_in_].fillna(0)
    # Si no existe la columna, recrearla según la lógica original
    if "Label" not in df.columns:
        df['Label'] = 'Sólida'
        df.loc[df['Net Income_Income Statement'] < 0, 'Label'] = 'Riesgosa'
        df.loc[
            (df['Net Income_Income Statement'] >= 0) &
            (df['Return on Equity_Key Ratios'] < 5), 'Label'
        ] = 'Estable'
    
    y = df["Label"]

    y_encoded = le.transform(y)
    y_pred = clf.predict(X)

    # 🧪 Métricas de clasificación
    st.subheader("📋 Reporte de Clasificación")
    report = classification_report(y_encoded, y_pred, target_names=le.classes_, output_dict=True)
    st.dataframe(pd.DataFrame(report).transpose().round(3))

    # 🔍 Matriz de Confusión
    st.subheader("🧱 Matriz de Confusión")
    conf_matrix = confusion_matrix(y_encoded, y_pred)

    fig, ax = plt.subplots()
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=le.classes_, yticklabels=le.classes_)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Valor real")
    ax.set_title("Matriz de Confusión")
    st.pyplot(fig)

    # 🎯 Importancia de variables
    st.subheader("📊 Importancia de Variables (Top 15)")
    importancias = pd.Series(clf.feature_importances_, index=clf.feature_names_in_).sort_values(ascending=False).head(15)

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.barplot(x=importancias, y=importancias.index, ax=ax2)
    ax2.set_title("Principales variables del modelo")
    ax2.set_xlabel("Importancia relativa")
    ax2.set_ylabel("Variables")
    st.pyplot(fig2)

# Para uso directo
if __name__ == "__main__":
    modelo_ui()

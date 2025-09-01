# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 19:20:12 2025

@author: luisa
"""

# ✅ Paso 1: Importación de librerías necesarias
import pandas as pd
import numpy as np

# ✅ Paso 2: Cargar el dataset desde archivo CSV
ruta = r"C:\Users\luisa\OneDrive\Escritorio\Master UCM\TFM\TFM_Propuesto\Dataset\00_dataset_tfm.csv"

try:
    df = pd.read_csv(ruta)
    print("✅ Dataset cargado correctamente. Dimensiones:", df.shape)
except Exception as e:
    print("❌ Error al cargar el dataset:", e)

# ✅ Paso 3: Exploración inicial del dataset

print("\n✅ Primeras 5 filas del dataset:")
print(df.head())

print("\n✅ Columnas disponibles:")
print(df.columns.tolist())

print("\n✅ Tipos de datos:")
print(df.dtypes)

print("\n✅ Valores nulos por columna:")
print(df.isnull().sum())

# ✅ Paso 4: Preparar copia del dataset para limpieza
df_clean = df.copy()

# ✅ Paso 5: Identificar columnas por tipo
NON_NUMERIC_COLS = ['ID', 'Ticker', 'Year']

cols_with_dollar = [
    col for col in df_clean.columns
    if '$' in col or 'per share' in col.lower()
]

cols_with_percent = [
    col for col in df_clean.columns
    if '%' in col or 'margin' in col.lower() or 'ratio' in col.lower()
]

numeric_cols = [
    col for col in df_clean.columns
    if col not in NON_NUMERIC_COLS + cols_with_dollar + cols_with_percent
]

# ✅ Paso 6: Funciones de limpieza

def clean_millions(value):
    """Limpia valores numéricos en millones."""
    if isinstance(value, str):
        value = value.replace(',', '').replace('−', '-').replace('–', '-').strip()
        if value in ['', '-', '--']:
            return np.nan
    try:
        return float(value)
    except Exception:
        return np.nan


def clean_percent(value):
    """Limpia valores porcentuales, eliminando % y adaptando decimales."""
    if isinstance(value, str):
        value = value.replace('%', '').replace(',', '.').strip()
        if value in ['', '-', '--']:
            return np.nan
    try:
        return float(value)
    except Exception:
        return np.nan


def clean_dollar(value):
    """Limpia valores en dólares o por acción."""
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '').strip()
        if value in ['', '-', '--']:
            return np.nan
    try:
        return float(value)
    except Exception:
        return np.nan

# ✅ Paso 7: Aplicar limpieza a columnas numéricas (millones)
for col in numeric_cols:
    df_clean[col] = df_clean[col].apply(clean_millions)

# ✅ Paso 8: Aplicar limpieza a columnas con porcentajes
for col in cols_with_percent:
    df_clean[col] = df_clean[col].apply(clean_percent)

# ✅ Paso 9: Aplicar limpieza a columnas con dólares / EPS
for col in cols_with_dollar:
    df_clean[col] = df_clean[col].apply(clean_dollar)

# ✅ Paso 10: Convertir columna Year a tipo entero
df_clean['Year'] = pd.to_numeric(df_clean['Year'], errors='coerce').astype('Int64')

# ✅ Paso 11: Revisión final de tipos y dimensiones
print("\n✅ Tipos de datos tras limpieza:")
print(df_clean.dtypes.value_counts())

print("\n✅ Dimensiones tras limpieza:", df_clean.shape)

# ✅ Paso 12: Tratamiento de valores nulos y filtrado de columnas

# Paso 12.1: Eliminar columnas con más del 40% de valores nulos
umbral_col_nulos = 0.4
cols_nulos_40 = df_clean.columns[df_clean.isnull().mean() > umbral_col_nulos].tolist()
df_clean.drop(columns=cols_nulos_40, inplace=True)

# Paso 12.2: Eliminar columnas constantes (sin variación)
cols_constantes = df_clean.columns[df_clean.nunique(dropna=False) <= 1].tolist()
df_clean.drop(columns=cols_constantes, inplace=True)

# Paso 12.3: Eliminar filas con más del 50% de valores nulos
umbral_fila_nulos = 0.5
df_clean = df_clean[df_clean.isnull().mean(axis=1) < umbral_fila_nulos]

# Paso 12.4: Recalcular columnas numéricas tras el filtrado
col_num_actualizadas = [
    col for col in df_clean.columns if col not in NON_NUMERIC_COLS
]

# Paso 12.5: Imputación por media de empresa (Ticker)
df_clean[col_num_actualizadas] = df_clean.groupby('Ticker')[col_num_actualizadas].transform(
    lambda x: x.fillna(x.mean())
)

# Paso 12.6: Imputación global para valores que aún queden
df_clean.fillna(df_clean.mean(numeric_only=True), inplace=True)

# ✅ Paso 13: Log final del tratamiento

print("\n🗑 Columnas eliminadas por tener más del 40% de valores nulos:")
for col in cols_nulos_40:
    print(" -", col)

print("\n🧹 Columnas eliminadas por ser constantes:")
if cols_constantes:
    for col in cols_constantes:
        print(" -", col)
else:
    print(" (Ninguna)")

print("\n🧬 Imputación aplicada en 2 fases:")
print(" - Primero por media dentro de cada empresa (Ticker)")
print(" - Luego por media global para los valores restantes")

print("\n📊 Resultado final del dataset limpio:")
print(f" - Filas conservadas: {df_clean.shape[0]}")
print(f" - Columnas finales útiles: {df_clean.shape[1]}")

# ✅ Paso final: Guardar dataset depurado a CSV
output_path = r"C:\Users\luisa\OneDrive\Escritorio\Master UCM\TFM\TFM_Propuesto\Dataset\01_dataset_depurado.csv"

try:
    df_clean.to_csv(output_path, index=False)
    print(f"\n✅ Dataset depurado guardado correctamente como: {output_path}")
except Exception as e:
    print("❌ Error al guardar el archivo:", e)


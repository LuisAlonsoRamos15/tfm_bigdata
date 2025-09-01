# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 11:42:07 2025

@author: luisa
"""

# clasificador_empresas.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ 1. Cargar el dataset depurado
df = pd.read_csv("01_dataset_depurado.csv")

# ✅ 2. Generar la columna 'Label' basada en Net Income y ROE
df['Label'] = 'Sólida'
df.loc[df['Net Income_Income Statement'] < 0, 'Label'] = 'Riesgosa'
df.loc[(df['Net Income_Income Statement'] >= 0) & (df['Return on Equity_Key Ratios'] < 5), 'Label'] = 'Estable'

# ✅ 3. Seleccionar variables numéricas como features
features = df.select_dtypes(include='number').drop(columns=['Year'], errors='ignore')
X = features
y = df['Label']

# ✅ 4. Codificar las etiquetas
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# ✅ 5. Dividir el dataset en entrenamiento y test
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.25, random_state=42)

# ✅ 6. Entrenar modelo Random Forest
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# ✅ 7. Evaluar el modelo
y_pred = clf.predict(X_test)
report = classification_report(y_test, y_pred, target_names=le.classes_)
conf_matrix = confusion_matrix(y_test, y_pred)

print("✅ Clasificación completada:\n")
print(report)

# ✅ 8. Guardar el modelo y el codificador
joblib.dump(clf, "modelo_clasificador.pkl")
joblib.dump(le, "label_encoder.pkl")
print("✅ Modelo y codificador guardados como .pkl")

# ✅ 9. Mostrar matriz de confusión
plt.figure(figsize=(6, 4))
sns.heatmap(conf_matrix, annot=True, fmt="d", xticklabels=le.classes_, yticklabels=le.classes_, cmap="Blues")
plt.title("Matriz de Confusión")
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.tight_layout()
plt.show()

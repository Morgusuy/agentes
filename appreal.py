import streamlit as st
import pandas as pd
import csv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
from datetime import datetime

# Autenticación con Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"]), scopes=SCOPE
)
client = gspread.authorize(credentials)

# Usamos el nombre de la planilla
worksheet = client.open("registro_actividades_agentes").sheet1

# Leer usuarios desde el CSV
def cargar_usuarios():
    usuarios = []
    with open("usuarios.csv", newline='', encoding='utf-8') as csvfile:
        lector = csv.reader(csvfile)
        next(lector)  # saltar encabezado
        for fila in lector:
            usuarios.append({"usuario": fila[0], "contraseña": fila[1], "nombre": fila[2]})
    return usuarios

usuarios = cargar_usuarios()

# Interfaz de login
st.title("Registro de Actividades - RE/MAX Real")
usuario_input = st.text_input("Usuario")
password_input = st.text_input("Contraseña", type="password")
usuario_actual = next((u for u in usuarios if u["usuario"] == usuario_input and u["contraseña"] == password_input), None)

if usuario_actual:
    st.success(f"Bienvenido {usuario_actual['nombre']} 👋")
    
    actividad = st.selectbox("Tipo de actividad", [
        "Llamada", "Reunión", "Publicación", "Visita", "Cierre", "Otro"
    ])
    
    descripcion = st.text_area("Descripción breve")
    
    requiere_seguimiento = st.radio("¿Requiere seguimiento?", ("Sí", "No"))
    fecha_seguimiento = None
    if requiere_seguimiento == "Sí":
        fecha_seguimiento = st.date_input("¿Para qué día?")

    if st.button("Registrar actividad"):
        fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            usuario_actual["nombre"],
            actividad,
            descripcion,
            requiere_seguimiento,
            fecha_seguimiento.strftime("%Y-%m-%d") if fecha_seguimiento else ""
        ]
        worksheet.append_row(fila)
        st.success("✅ Actividad registrada con éxito")
else:
    st.warning("Ingresá tus credenciales para continuar.")

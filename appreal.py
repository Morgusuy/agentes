import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---------------------- CONFIGURACIÓN ----------------------

st.set_page_config(page_title="CRM Agentes", page_icon="📋", layout="centered")

# Autenticación con Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"]), scopes=SCOPE
)
gc = gspread.authorize(credentials)
SHEET_NAME = "crm_data"
worksheet = gc.open(SHEET_NAME).sheet1

# ---------------------- LOGIN ----------------------

st.title("🔐 Acceso al CRM de Agentes")

if "login_success" not in st.session_state:
    st.session_state.login_success = False

if not st.session_state.login_success:
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")

        if submitted:
            usuarios_validos = st.secrets["USUARIOS"]
            if usuario in usuarios_validos and usuarios_validos[usuario] == password:
                st.session_state.login_success = True
                st.session_state.usuario = usuario
                st.success("Ingreso correcto.")
            else:
                st.error("Usuario o contraseña incorrectos.")

# ---------------------- FORMULARIO ----------------------

if st.session_state.login_success:
    st.header(f"📋 Registro de Actividad - {st.session_state.usuario}")

    actividad = st.selectbox("Tipo de actividad", [
        "Llamada", "Reunión", "WhatsApp", "Email", "Visita a propiedad", "Publicación", "Otro"
    ])

    descripcion = st.text_area("Descripción de la actividad")

    requiere_seguimiento = st.radio("¿Requiere seguimiento?", ["Sí", "No"])

    fecha_seguimiento = None
    if requiere_seguimiento == "Sí":
        fecha_seguimiento = st.date_input("¿Fecha de seguimiento?")

    if st.button("Registrar actividad"):
        if requiere_seguimiento == "Sí" and not fecha_seguimiento:
            st.warning("Debes ingresar una fecha de seguimiento.")
        else:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila = [
                fecha_hora,
                st.session_state.usuario,
                actividad,
                descripcion,
                requiere_seguimiento,
                str(fecha_seguimiento) if fecha_seguimiento else ""
            ]
            worksheet.append_row(fila)
            st.success("✅ Actividad registrada correctamente.")

    with st.expander("📈 Ver últimas 10 actividades"):
        df = pd.DataFrame(worksheet.get_all_records())
        df_usuario = df[df["Agente"] == st.session_state.usuario]
        st.dataframe(df_usuario.tail(10))

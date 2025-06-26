import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---------- CONFIGURACIÓN GOOGLE SHEETS ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["GOOGLE_SERVICE_ACCOUNT"], scopes=SCOPE
)

gc = gspread.authorize(credentials)
SHEET_NAME = "registro_actividades_agentes"  # ¡Tu hoja de Google!
worksheet = gc.open(SHEET_NAME).sheet1

# ---------- INTERFAZ PRINCIPAL ----------
st.set_page_config(page_title="Registro de Actividades", layout="centered")
st.title("📝 Registro Diario de Actividades")

# ---------- LOGIN BÁSICO ----------
st.subheader("🔐 Ingreso del agente")

usuarios_df = pd.read_csv("usuarios.csv")
usuarios = usuarios_df["usuario"].tolist()
usuario_seleccionado = st.selectbox("Seleccioná tu nombre", usuarios)
clave = st.text_input("Contraseña", type="password")

usuario_correcto = usuarios_df[usuarios_df["usuario"] == usuario_seleccionado]
if not usuario_correcto.empty and clave == usuario_correcto["clave"].values[0]:
    st.success(f"Bienvenido, {usuario_seleccionado}")

    # ---------- FORMULARIO DE ACTIVIDAD ----------
    st.subheader("📌 Nueva Actividad")

    tipo = st.selectbox("Tipo de actividad", [
        "Llamada telefónica", "Reunión presencial", "Publicación en redes",
        "Captación", "Visita a propiedad", "Seguimiento", "Otra"
    ])

    descripcion = st.text_area("Descripción breve", max_chars=200)
    requiere_seguimiento = st.radio("¿Requiere seguimiento?", ["Sí", "No"])

    fecha_seguimiento = ""
    if requiere_seguimiento == "Sí":
        fecha_seguimiento = st.date_input("Fecha de seguimiento")

    if st.button("Registrar actividad"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fila = [
            now,
            usuario_seleccionado,
            tipo,
            descripcion,
            requiere_seguimiento,
            fecha_seguimiento if requiere_seguimiento == "Sí" else ""
        ]
        worksheet.append_row(fila)
        st.success("✅ Actividad registrada correctamente")

else:
    st.warning("Ingresá tus credenciales para continuar")

# ---------- VISTA BROKER (opcional) ----------
if usuario_seleccionado == "Gustavo Moreira" and clave == usuario_correcto["clave"].values[0]:
    st.subheader("📊 Vista broker")
    df = pd.DataFrame(worksheet.get_all_records())
    st.dataframe(df.sort_values("fecha", ascending=False), use_container_width=True)

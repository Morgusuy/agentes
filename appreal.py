import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime

# ---------- CONFIG GOOGLE SHEETS ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"]), scopes=SCOPE
)
gc = gspread.authorize(credentials)

# Nombre de tu spreadsheet y hoja (cámbialo si usas otro)
SHEET_NAME = "registro_actividades_agentes"
worksheet = gc.open(SHEET_NAME).sheet1

# ---------- CARGAR USUARIOS ----------
# usuarios.csv debe tener columnas: usuario,contraseña,nombre
usuarios_df = pd.read_csv("usuarios.csv")
auth = {
    row["usuario"]: (str(row["contraseña"]), row["nombre"])
    for _, row in usuarios_df.iterrows()
}

# ---------- LOGIN ----------
st.set_page_config(page_title="CRM Agentes", layout="centered")
st.title("🔐 Login CRM RE/MAX Real")

if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    with st.form("login"):
        alias = st.text_input("Usuario")
        passwd = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Ingresar")

    if ok:
        if alias in auth and passwd == auth[alias][0]:
            st.session_state.logged = True
            st.session_state.alias = alias
            st.session_state.nombre = auth[alias][1]
            st.success(f"Bienvenido, {st.session_state.nombre}")
        else:
            st.error("Alias o contraseña incorrectos.")

# ---------- FORMULARIO DE ACTIVIDAD ----------
if st.session_state.get("logged", False):
    st.header("📋 Registrar nueva actividad")

    tipo = st.selectbox(
        "Tipo de actividad",
        ["Llamada", "Reunión", "WhatsApp", "Email",
         "Visita a propiedad", "Publicación", "Otro"],
    )
    descripcion = st.text_area("Descripción")
    seguimiento = st.radio("¿Requiere seguimiento?", ("No", "Sí"))
    fecha_seg = ""
    if seguimiento == "Sí":
        fecha_seg = st.date_input("Fecha de seguimiento").strftime("%Y-%m-%d")

    if st.button("Guardar actividad"):
        if not descripcion:
            st.warning("🔔 Describe brevemente la actividad.")
        elif seguimiento == "Sí" and not fecha_seg:
            st.warning("🔔 Selecciona la fecha de seguimiento.")
        else:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state.nombre,           # nombre completo
                tipo,
                descripcion,
                seguimiento,
                fecha_seg,
            ]
            worksheet.append_row(row)
            st.success("✅ Actividad registrada.")

    # ---------- HISTÓRICO DEL AGENTE ----------
    with st.expander("📈 Mis últimas 10 actividades"):
        df = pd.DataFrame(worksheet.get_all_records())
        mine = df[df["Agente"] == st.session_state.nombre].tail(10)
        st.dataframe(mine, use_container_width=True)

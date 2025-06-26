import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------- CONFIGURACIÓN ----------
USUARIOS_FILE = "usuarios.csv"
DATA_FILE = "streamlit_crm_base.csv"

# ---------- CARGAR USUARIOS ----------
usuarios_df = pd.read_csv(USUARIOS_FILE)

# ---------- LOGIN ----------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_nombre = ""

if not st.session_state.autenticado:
    st.title("Ingreso al CRM de Agentes")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        fila = usuarios_df[
            (usuarios_df["usuario"] == usuario) &
            (usuarios_df["contraseña"] == contraseña)
        ]
        if not fila.empty:
            st.session_state.autenticado = True
            st.session_state.usuario_nombre = fila.iloc[0]["nombre"]
            st.success(f"Bienvenido, {st.session_state.usuario_nombre}")
        else:
            st.error("Usuario o contraseña incorrectos.")
    st.stop()

# ---------- FUNCIONES AUXILIARES ----------

def guardar_datos(nueva_fila):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    else:
        df = pd.DataFrame([nueva_fila])
    df.to_csv(DATA_FILE, index=False)

# ---------- FORMULARIO ----------
st.title("Registro de Actividades")
st.markdown("Completa tu actividad para que el broker vea tu progreso.")

actividad = st.selectbox("Tipo de actividad", [
    "Llamada a lead",
    "Mensaje por WhatsApp",
    "Publicación en redes",
    "Captación",
    "Reunión presencial",
    "Seguimiento",
    "Otro"
])

detalle = st.text_area("Descripción breve de la actividad")

requiere_seguimiento = st.radio("¿Requiere seguimiento?", ["Sí", "No"])

fecha_seguimiento = None
if requiere_seguimiento == "Sí":
    fecha_seguimiento = st.date_input("¿Cuándo hay que hacer el seguimiento?")

# ---------- BOTÓN DE ENVÍO ----------
if st.button("Registrar actividad"):
    if actividad and detalle:
        nueva_fila = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agente": st.session_state.usuario_nombre,
            "actividad": actividad,
            "detalle": detalle,
            "requiere_seguimiento": requiere_seguimiento,
            "fecha_seguimiento": fecha_seguimiento if requiere_seguimiento == "Sí" else ""
        }
        guardar_datos(nueva_fila)
        st.success("✅ Actividad registrada correctamente.")
    else:
        st.warning("🛑 Debes completar la actividad y descripción antes de enviar.")

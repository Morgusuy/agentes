import streamlit as st
import pandas as pd
from datetime import date, datetime

DATA_FILE = "streamlit_crm_base.csv"

# --- Lista de agentes válidos ---
AGENTES_VALIDOS = ["Malena Pérez Abad", "Cynthia Moreira", "Alain Montans", "Carolina Balbuena", "Lilia Echarte", "Federico Sierra", "Daniel Oyola"]

# --- Login simple ---
st.set_page_config(page_title="CRM RE/MAX Real", layout="centered")
st.title("🧭 CRM de Actividad - RE/MAX Real")

agente = st.selectbox("Seleccioná tu nombre", ["Seleccionar..."] + AGENTES_VALIDOS)

if agente != "Seleccionar...":
    st.success(f"Bienvenido/a, {agente}")
    
    st.subheader("📋 Nueva Actividad")

    with st.form("formulario_actividad"):
        fecha_actividad = st.date_input("📅 Fecha de la actividad", date.today())
        tipo_actividad = st.selectbox("🎯 Tipo de actividad", ["Llamada", "Mensaje", "Reunión", "Visita", "Publicación", "Otro"])
        nombre_contacto = st.text_input("👤 Nombre del contacto")
        descripcion = st.text_area("📝 Breve descripción de la actividad")

        seguimiento = st.radio("📌 ¿Requiere seguimiento?", ["No", "Sí"])
        if seguimiento == "Sí":
            fecha_seguimiento = st.date_input("📆 Fecha de seguimiento", date.today())
            motivo = st.text_input("📣 Motivo del seguimiento")
        else:
            fecha_seguimiento = ""
            motivo = ""

        resultado = st.selectbox("📊 Resultado", ["Interesado", "Sin interés", "No contesta", "Agendar llamada", "Otro"])

        enviado = st.form_submit_button("✅ Guardar actividad")

        if enviado:
            nuevo_registro = pd.DataFrame([{
                "Marca de tiempo": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Agente": agente,
                "Fecha de actividad": fecha_actividad,
                "Tipo de actividad": tipo_actividad,
                "Nombre del contacto": nombre_contacto,
                "Descripción": descripcion,
                "Requiere seguimiento": seguimiento,
                "Fecha de seguimiento": fecha_seguimiento,
                "Motivo del seguimiento": motivo,
                "Resultado": resultado
            }])

            try:
                datos_existentes = pd.read_csv(DATA_FILE)
                df_final = pd.concat([datos_existentes, nuevo_registro], ignore_index=True)
            except FileNotFoundError:
                df_final = nuevo_registro

            df_final.to_csv(DATA_FILE, index=False)
            st.success("✅ Actividad registrada correctamente")

    # Mostrar actividades anteriores del agente
    st.subheader("📈 Mis actividades registradas")
    try:
        df = pd.read_csv(DATA_FILE)
        df_agente = df[df["Agente"] == agente]
        st.dataframe(df_agente.sort_values("Marca de tiempo", ascending=False), use_container_width=True)
    except FileNotFoundError:
        st.info("Aún no hay actividades registradas.")
else:
    st.warning("👀 Seleccioná tu nombre para comenzar")

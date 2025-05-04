import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai_key"])

st.set_page_config(page_title="Chat de Resumen Diario", layout="centered")
st.title("💬 Chat con el Resumen del Día")

# Inicializar historial y contexto
if "historial" not in st.session_state:
    st.session_state.historial = []
if "contexto" not in st.session_state:
    st.session_state.contexto = ""
if "cargado" not in st.session_state:
    st.session_state.cargado = False

st.markdown("Primero, sube un archivo `.txt` con los mensajes del día (uno por línea):")
archivo = st.file_uploader("Subir archivo", type="txt")

if archivo is not None and not st.session_state.cargado:
    mensajes = archivo.read().decode("utf-8").splitlines()
    contenido_mensajes = "\n".join([f"- {m}" for m in mensajes])

    st.session_state.contexto = f"""
Has recibido las siguientes conversaciones internas entre trabajadores hoy. Tu tarea es actuar como un asistente profesional que prepara un informe diario para el presidente de la empresa.

Analiza todos los mensajes. Ignora lo trivial (como fiestas, comida, charlas personales), y enfócate en lo que el presidente necesita saber:
- Problemas importantes
- Avances clave
- Riesgos
- Decisiones críticas
- Cualquier hecho que merezca su atención

Aquí están los mensajes de hoy:
{contenido_mensajes}
"""
    st.session_state.cargado = True
    st.success("📥 Archivo cargado correctamente. Ya puedes hacer preguntas sobre el día.")

if st.session_state.cargado:
    pregunta = st.text_input("Haz una pregunta sobre lo que pasó hoy:")

    if pregunta:
        mensajes = [
            {"role": "system", "content": "Eres un asistente profesional que responde preguntas sobre el resumen diario de una empresa."},
            {"role": "user", "content": st.session_state.contexto}
        ]

        for entrada in st.session_state.historial:
            mensajes.append({"role": "user", "content": entrada["usuario"]})
            mensajes.append({"role": "assistant", "content": entrada["ia"]})

        mensajes.append({"role": "user", "content": pregunta})

        try:
            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=mensajes,
                temperature=0.7
            )
            texto_respuesta = respuesta.choices[0].message.content
            st.session_state.historial.append({"usuario": pregunta, "ia": texto_respuesta})

            st.markdown("### 🤖 Respuesta:")
            st.write(texto_respuesta)
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if st.session_state.historial:
        st.markdown("---")
        st.markdown("### 🕒 Historial de la conversación")
        for entrada in reversed(st.session_state.historial):
            st.markdown(f"**Tú:** {entrada['usuario']}")
            st.markdown(f"**Asistente:** {entrada['ia']}")



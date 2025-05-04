import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai_key"])

st.set_page_config(page_title="Chat de Resumen Diario", layout="centered")
st.title("💬 Chat con el Resumen del Día")

# Inicializar historial y contexto
if "historial" not in st.session_state:
    st.session_state.historial = []
    st.session_state.contexto = ""
    st.session_state.cargado = False

st.markdown("Primero, sube un archivo `.txt` con los mensajes del día (uno por línea):")
archivo = st.file_uploader("Subir archivo", type="txt")

if archivo is not None and not st.session_state.cargado:
    lineas = archivo.read().decode("utf-8").splitlines()
    bloques = [lineas[i:i+200] for i in range(0, len(lineas), 200)]
    resumenes = []

    for i, bloque in enumerate(bloques):
        bloque_texto = "\n".join([f"- {m}" for m in bloque])
        prompt_resumen = f"""
Tienes los siguientes mensajes internos de una empresa que exporta frutas:
{bloque_texto}

Resume solo lo importante en 5-8 líneas. No repitas trivialidades. Si hay tareas, reclamaciones, problemas o avances, inclúyelos.
"""
        try:
            respuesta_bloque = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en logística y operaciones que resume mensajes empresariales."},
                    {"role": "user", "content": prompt_resumen}
                ],
                temperature=0.4,
                max_tokens=300
            )
            resumenes.append(respuesta_bloque.choices[0].message.content)
        except Exception as e:
            resumenes.append(f"[ERROR en bloque {i+1}: {str(e)}]")

    resumen_completo = "\n".join(resumenes)
    st.session_state.contexto = f"""Este es el resumen general del día basado en todos los mensajes:
{resumen_completo}
"""
    st.session_state.historial.append({
        "usuario": "[Sistema]",
        "ia": "Hola jefe, he resumido todos los mensajes del día. ¿Qué desea saber primero?"
    })
    st.session_state.cargado = True
    st.success("📥 Archivo procesado y resumido correctamente. Ya puedes hacer preguntas.")

# Mostrar historial tipo chat + campo de entrada
if st.session_state.cargado:
    st.markdown("---")
    st.markdown("### 🧾 Conversación")
    for entrada in st.session_state.historial:
        if entrada["usuario"] != "[Sistema]":
            st.chat_message("user").markdown(entrada["usuario"])
        st.chat_message("assistant").markdown(entrada["ia"])

    pregunta = st.chat_input("Haz una pregunta sobre lo que pasó hoy:")

    if pregunta:
        mensajes = [
            {"role": "system", "content": "Eres un asistente profesional que responde de forma breve y clara a preguntas sobre el resumen diario de una empresa exportadora de frutas. Incluye consejos si es útil."},
            {"role": "user", "content": st.session_state.contexto}
        ]
        for entrada in st.session_state.historial:
            if entrada["usuario"] != "[Sistema]":
                mensajes.append({"role": "user", "content": entrada["usuario"]})
                mensajes.append({"role": "assistant", "content": entrada["ia"]})

        mensajes.append({"role": "user", "content": pregunta})

        try:
            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=mensajes,
                temperature=0.5,
                max_tokens=500
            )
            texto_respuesta = respuesta.choices[0].message.content
            st.session_state.historial.append({"usuario": pregunta, "ia": texto_respuesta})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")


import streamlit as st
import openai

openai.api_key = st.secrets["openai_key"]

st.set_page_config(page_title="Resumen Diario", layout="centered")
st.title("📋 Resumen Inteligente de Mensajes Diarios")

st.markdown("Pegue aquí los mensajes internos del día (uno por línea):")
entrada = st.text_area("Mensajes del día", height=300)

if st.button("Generar resumen"):
    if not entrada.strip():
        st.warning("Por favor, ingresa algunos mensajes.")
    else:
        mensajes = entrada.strip().split("\n")

        prompt = f"""
Has recibido las siguientes conversaciones internas entre trabajadores hoy. Tu tarea es actuar como un asistente profesional que prepara un informe diario para el presidente de la empresa.

Analiza todos los mensajes. Ignora lo trivial (como fiestas, comida, charlas personales), y enfócate en lo que el presidente necesita saber:
- Problemas importantes
- Avances clave
- Riesgos
- Decisiones críticas
- Cualquier hecho que merezca su atención

Escribe un resumen humano, profesional, natural y variado. No digas que estás resumiendo, simplemente cuéntale lo que pasó de manera clara y directa.

Aquí están los mensajes de hoy:
{chr(10).join(['- ' + m for m in mensajes])}
"""

        try:
            respuesta = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente profesional que redacta informes para el presidente de una empresa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            resumen = respuesta['choices'][0]['message']['content']
            st.subheader("📝 Resumen generado:")
            st.write(resumen)
        except Exception as e:
            st.error(f"Error: {str(e)}")


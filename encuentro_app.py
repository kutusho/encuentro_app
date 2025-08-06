import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
import os
from datetime import datetime

DATA_PATH = 'data/asistentes.csv'
os.makedirs('data', exist_ok=True)

def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=['Nombre', 'Email', 'Institucion', 'QR_ID', 'Fecha_Registro', 'Hora_Checkin'])

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

def show_program():
    st.subheader("Programa del Encuentro")
    tabs = st.tabs(["11 de Noviembre", "12 de Noviembre", "13 de Noviembre"])
    with tabs[0]:
        st.markdown("""
        - **09:00** Registro  
        - **10:00** Inauguración  
        - **11:00** Conferencia magistral: *La mujer en la historia del turismo* - Dra. Fanny López  
        - **13:00** Comida  
        - **15:00** Panel de expertos: *Turismo cultural y natural*
        """)
    with tabs[1]:
        st.markdown("""
        - **09:00** Talleres simultáneos  
        - **13:00** Comida  
        - **15:00** Actividad cultural
        """)
    with tabs[2]:
        st.markdown("""
        - **08:00** Salida a Chiapa de Corzo y Cañón del Sumidero  
        - **14:00** Clausura y reconocimientos
        """)

def registro():
    st.subheader("Registro de Participantes")
    with st.form("form_registro"):
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico")
        institucion = st.text_input("Institución o dependencia")
        enviado = st.form_submit_button("Generar QR")

        if enviado and nombre and email:
            df = load_data()
            qr_id = f"ID-{len(df)+1}-{nombre[:3].upper()}"
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            qr_img = generate_qr_code(qr_id)
            new_row = {
                'Nombre': nombre,
                'Email': email,
                'Institucion': institucion,
                'QR_ID': qr_id,
                'Fecha_Registro': fecha,
                'Hora_Checkin': ''
            }
            df = df.append(new_row, ignore_index=True)
            save_data(df)
            st.success("Registro exitoso. Aquí está tu código QR:")
            buf = BytesIO()
            qr_img.save(buf)
            st.image(buf.getvalue(), width=200)

def check_in():
    st.subheader("Check-in de Participantes")
    qr_code = st.text_input("Escanea o ingresa el código QR:")
    if qr_code:
        df = load_data()
        if qr_code in df['QR_ID'].values:
            df.loc[df['QR_ID'] == qr_code, 'Hora_Checkin'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_data(df)
            st.success("✅ Check-in registrado.")
            participante = df[df['QR_ID'] == qr_code].iloc[0]
            st.write(f"Bienvenido(a), {participante['Nombre']} de {participante['Institucion']}")
        else:
            st.error("❌ QR no reconocido.")

def admin_panel():
    st.subheader("Panel Administrativo")
    df = load_data()
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar lista de asistentes", csv, file_name="asistentes.csv")

st.set_page_config(page_title="Encuentro de Guías", layout="centered")
st.title("📍 Primer Encuentro Internacional de Guías de Turistas")
st.caption("11 al 13 de noviembre de 2025 | Tuxtla Gutiérrez, Chiapas")

menu = st.sidebar.radio("Navegación", ["Inicio", "Programa", "Registro", "Check-in", "Panel Admin"])

if menu == "Inicio":
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Logo_SECTUR_M%C3%A9xico.png/800px-Logo_SECTUR_M%C3%A9xico.png", width=200)
    st.markdown("Bienvenido al sistema de gestión del evento. Usa el menú de la izquierda para navegar.")

elif menu == "Programa":
    show_program()

elif menu == "Registro":
    registro()

elif menu == "Check-in":
    check_in()

elif menu == "Panel Admin":
    admin_panel()

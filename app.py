import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import paho.mqtt.client as paho
import json

# Función de callback para publicación MQTT
def on_publish(client, userdata, result):
    print("El dato ha sido publicado \n")
    pass

# Función de callback para recepción MQTT
def on_message(client, userdata, message):
    global message_received
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"Mensaje recibido: {message_received}")

# Configuración del cliente MQTT
broker = "157.230.214.127"  # Dirección del broker MQTT
port = 1883  # Puerto del broker MQTT
client1 = paho.Client("plumas")  # Nombre del cliente MQTT
client1.on_publish = on_publish
client1.on_message = on_message

# Título y descripción en la aplicación Streamlit
st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

# Mostrar imagen de cabecera
image = Image.open("voice_ctrl.jpg")
st.image(image, width=200)

# Botón para el control por voz
st.write("Toca el Botón y habla")
stt_button = Button(label="Inicio", width=200)

# Configuración del reconocimiento de voz
stt_button.js_on_event(
    "button_click",
    CustomJS(
        code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        };
        recognition.start();
    """
    ),
)

# Procesar eventos del botón
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

if result:
    if "GET_TEXT" in result:
        # Capturar texto reconocido
        command = result.get("GET_TEXT").strip()
        st.write(f"Comando recibido: {command}")

        # Conexión al broker MQTT y publicación del mensaje
        try:
            client1.connect(broker, port)  # Conexión al broker MQTT
            message = json.dumps({"Act1": command})  # Crear mensaje JSON
            st.write(f"Mensaje publicado: {message}")
            ret = client1.publish("voice_plumas", message)  # Publicar mensaje al topic
            
            # Verificar éxito de la publicación
            if ret[0] == 0:
                st.success("Mensaje enviado al ESP32 correctamente.")
            else:
                st.error("Error al publicar el mensaje MQTT.")
        except Exception as e:
            st.error(f"Error en la conexión MQTT: {e}")

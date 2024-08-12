# Librerias necesarias
from openai import OpenAI

# DICCIONARIO PARA LAS CONVERSACIONES
conversaciones = {}

##############################################
# COMUNICACION CON OPENAI
##############################################
def almacenar_mensaje(usuario_id, mensaje, es_bot=False):
    if usuario_id not in conversaciones:
        conversaciones[usuario_id] = []
    prefijo = "Bot: " if es_bot else "Usuario: "
    conversaciones[usuario_id].append(prefijo + mensaje)

def get_conversacion(id_usuario):
    conversacion = conversaciones.get(id_usuario, [])
    error = False

    if not conversacion:
        error = True
    else:
        respuesta = '\n'.join(conversacion)

    return respuesta, error
    

def get_chatGPT(id_usuario, tipo_cons, clima, audio):
    client = OpenAI()

    error = False

    if tipo_cons == 'clasificar':
        conversacion_texto, error = get_conversacion(id_usuario)
        pregunta = f'Quiero que analices esta conversacion entre un bot de telegram y un usuario y clasifiques el sentimiento entre positivo, negativo o neutro. A su vez quiero que me des una breve explicacion de por que elegiste eso. La conversacion es la siguiente: {conversacion_texto}'
    elif tipo_cons == 'clima':
        pregunta = f'Hoy hace un dia {clima} en Montevideo, Uruguay, tienes recomendaciones para hacer algo aqui con este clima? Y dame consejos determinados por el clima. Todo en no mas de 500 caracteres'
    elif tipo_cons == 'audio':
        transcripcion = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )
        texto_transcrito = transcripcion.text

        # Resumir el texto transcrito usando la API de OpenAI
        pregunta = f'Resume el siguiente texto: {texto_transcrito}'

    if not error:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente para un bot de telegram"},
                {"role": "user", "content": pregunta}
            ]
        )

    if tipo_cons == 'audio':
        return f'Audio transcripto\n{texto_transcrito}\n\nResumen: {response.choices[0].message.content}'
    else:
        return response.choices[0].message.content
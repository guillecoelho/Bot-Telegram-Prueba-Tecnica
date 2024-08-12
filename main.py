# Librerias necesarias
import telebot
from telebot import types
from dotenv import load_dotenv
import os
import requests
import json
import sqlite3
from funciones import get_chatGPT, almacenar_mensaje

# CARGO LOS TOKENS DE LAS APIs
load_dotenv()

TOKEN = os.getenv('TOKEN_TELEGRAM')
API_OPEN_WEATHER = os.getenv('API_OPEN_WEATHER')

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# CARGO DATOS PARA RECOMENDACIONES CON EL CLIMA
f = open('clima.json')

recomendaciones = json.load(f)["recomendaciones"][0]

f.close()

##############################################
# COMUNICACION CON OPENWEATHER
##############################################
URL_OPEN_WEATHER = 'https://api.openweathermap.org/data/2.5/weather?lang=es&units=metric&'

def get_weather():
    # Aqui se completa la url con los parametros restantes
    url_llamada = URL_OPEN_WEATHER + 'q=' + 'montevideo' + '&appid=' + API_OPEN_WEATHER
    response = requests.get(url_llamada)
    data = response.json()

    # Controlo si existe un error a la hora de llamar a la API
    error = False

    # El codigo de la request http es 200 cuando es correcto, 401 indica un error con el token de la api por eso se diferencia.
    if data["cod"] == 200:
        main_data = data["weather"][0]["main"]
        weather_data = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return weather_data, temp, main_data, error
    elif data["cod"] == 401:
        error = True
        return 'Problema con la API key', '', '', error
    else:
        error = True
        return 'Ocurrio un error con la solicitud', '', '', error

##############################################
# CONTADOR
##############################################
def incrementar_contador(id_usuario):
    # Conexión a la base de datos SQLite
    conn = sqlite3.connect('contador_usuarios.db')
    c = conn.cursor()

    # Crear tabla si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS contador_usuarios (
            id_usuario INTEGER PRIMARY KEY,
            contador INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

    # Verificar si el usuario ya existe en la base de datos
    c.execute('SELECT contador FROM contador_usuarios WHERE id_usuario = ?', (id_usuario,))
    fila = c.fetchone()

    if fila is None:
        # Insertar nuevo usuario con contador en 1
        c.execute('INSERT INTO contador_usuarios (id_usuario, contador) VALUES (?, ?)', (id_usuario, 1))
        contador = 1
    else:
        # Incrementar contador
        contador = fila[0] + 1
        c.execute('UPDATE contador_usuarios SET contador = ? WHERE id_usuario = ?', (contador, id_usuario))

    conn.commit()

    return contador

##############################################
# Funcionalidad extra para transcribir audios
##############################################
@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    # Descargar el archivo de audio
    file_info = bot.get_file(message.voice.file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
    audio_data = requests.get(file_url).content

    with open("audio.ogg", "wb") as audio_file:
        audio_file.write(audio_data)

    audio_file_path = "audio.ogg"
    audio_file = open(audio_file_path, "rb")

    respuesta = get_chatGPT('','audio','',audio_file)

    # Elimino el archivo de audio temporal
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)

    bot.reply_to(message, f'{respuesta}')

##############################################
############### MAIN HANDLES #################
##############################################
@bot.message_handler(commands=['start', 'help'])
def send_options(message):
    id_usuario = message.chat.id

    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn_clima = types.InlineKeyboardButton('¡Quiero saber el clima!', callback_data='clima')
    btn_contador = types.InlineKeyboardButton('¡Quiero contar!', callback_data='contador')
    btn_chat = types.InlineKeyboardButton('¿Que opina chatGPT de esta conversación?!', callback_data='chatgpt')

    markup.add(btn_clima, btn_contador, btn_chat)

    respuesta = '¡Hola! ¿Qué necesitas?\n\nRecuerda que si me envias un mensaje de audio puedo transcribirlo y resumirlo para ti.'

    almacenar_mensaje(id_usuario, respuesta, es_bot=True)
    bot.send_message(id_usuario, respuesta, reply_markup=markup)

##############################################
################# RESPONSES ##################
##############################################
@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    id_usuario = call.from_user.id

    if call.data == 'clima':
        almacenar_mensaje(id_usuario, '¡Quiero saber el clima!', es_bot=False)
        info, temp, main_data, error = get_weather()
        if error:
            respuesta = info
        else:
            respuesta = f"En Montevideo actualmente se experimenta {info} con una temperatura de {temp:.0f} grados.\n{recomendaciones[main_data]}"
            recomendacion_openai = get_chatGPT('','clima',info,'')
            respuesta = f'{respuesta}\n\n{recomendacion_openai}'
    elif call.data == 'contador':
        almacenar_mensaje(id_usuario, '¡Quiero contar!', es_bot=False)
        contador = incrementar_contador(call.from_user.id)
        respuesta = f"Actualmente tu contador es: {contador}"
    elif call.data == 'chatgpt':
        almacenar_mensaje(id_usuario, '¿Que opina chatGPT de esta conversación?!', es_bot=False)
        respuesta = get_chatGPT(id_usuario,'clasificar','','')
    
    almacenar_mensaje(id_usuario, respuesta, es_bot=True)
    bot.send_message(id_usuario, respuesta)

##############################################
################### MAIN #####################
##############################################
if __name__ == "__main__":
    print('Servidor de bot iniciado')
    if TOKEN:
        bot.infinity_polling()
    else:
        print('ERROR: Hace falta Token para el bot de telegram')
    print('Servidor de bot terminado')
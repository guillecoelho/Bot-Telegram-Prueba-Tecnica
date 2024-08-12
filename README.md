# Bot para Telegram con Python

## Prueba Técnica Hikko Julio 2024 - Crear un bot de Telegram que se conecte con las APIs de Open-Weather y OpenAI

El proyecto se basa en un servidor hecho con Python el cual se conecta con la API de Telegram. El mismo tiene 4 funcionalidades:

- Nos da el clima actual en la ciudad de Montevideo junto con recomendaciones dadas por servidor y por OpenAI.
- Puede almacenar contar los clicks que hace un usuario en la acción de quiero contar. Esta información es persistente luego de reiniciar el servidor.
- Podemos comunicarnos con OpenAI para que nos de una breve clasificación de la conversación que tenemos con el bot.
- Finalmente si envíamos un mensaje de audio el bot lo enviara a OpenAI para que lo transcriba y nos resuma el contenido del audio.

## Cómo usarlo

1. Clonar el repositorio
2. Obtener los tokens de la Api de telegram mediante BotFather (https://core.telegram.org/bots/tutorial#obtain-your-bot-token), una API Key de Open Weather (https://openweathermap.org/api) y de OpenAI (https://platform.openai.com/docs/overview)
3. Crear el archivo .env en la raíz del proyecto con el siguiente contenido y reemplazar "token" con sus correspondientes tokens:

```
TOKEN_TELEGRAM="token"
API_OPEN_WEATHER="token"
OPENAI_API_KEY="token"
```

4. Instalar las librerías neceasarias, todas estan listadas en el archivo requierments.txt: `pip install -r requierments.txt`
5. Ya podremos correr el servidor con una terminal y el siguiente comando: `python3 main.py`

Una vez que la consola nos imprima `Servidor de bot iniciado` ya estaremos listos para poder usar el bot en Telegram.

## Funcionalidad Extra:

- La realidad es que me encuentro más de una vez en la situación de recibir mensajes en audios y no poder escucharlos por lo que poder transcribirlos de forma precisa con un modelo como el de Whisper es un salvavidas. A su vez de vez en cuando recibo audios muy largos los cuales si estoy corto de tiempo tener la posibilidad de ver un breve resumen de su contenido es útil para saber si es una urgencia y debo atenderlo o puedo dejarlo para luego.

## Extras:

- El archivo clima.json contiente recomendaciones correspondientes a los diferentes climas posibles que pueden haber, en caso de querer cambiarlas simplemente modificar este archivo.
- La base de datos para el contador se encuentra en el archivo contador_usuarios.db

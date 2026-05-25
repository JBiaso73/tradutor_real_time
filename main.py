from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import os

app = FastAPI()

@app.get("/")
async def get_index():
    return FileResponse("index.html")

@app.get("/manifest.json")
async def get_manifest():
    return FileResponse("manifest.json")

@app.get("/sw.js")
async def get_sw():
    return FileResponse("sw.js", media_type="application/javascript")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            texto_ingles = await websocket.receive_text()
            
            # Faz a tradução
            texto_pt = GoogleTranslator(source='en', target='pt').translate(texto_ingles)
            
            # Gera o arquivo de áudio
            tts = gTTS(text=texto_pt, lang='pt', slow=False)
            arquivo_audio = "resposta.mp3"
            tts.save(arquivo_audio)
            
            # Transforma em Base64
            with open(arquivo_audio, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Envia TEXTO e ÁUDIO para o celular
            await websocket.send_json({
                "texto": texto_pt,
                "audio": audio_base64
            })
            
            os.remove(arquivo_audio)
    except WebSocketDisconnect:
        pass

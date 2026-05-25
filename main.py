from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import io

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
            
            # 1. Tradução
            texto_pt = GoogleTranslator(source='en', target='pt').translate(texto_ingles)
            
            # 2. Gera o áudio direto na memória RAM (MUITO mais rápido)
            tts = gTTS(text=texto_pt, lang='pt', slow=False)
            memoria_audio = io.BytesIO()
            tts.write_to_fp(memoria_audio)
            
            # 3. Converte e envia
            memoria_audio.seek(0)
            audio_base64 = base64.b64encode(memoria_audio.read()).decode('utf-8')
            
            await websocket.send_json({
                "texto": texto_pt,
                "audio": audio_base64
            })
            
    except WebSocketDisconnect:
        pass

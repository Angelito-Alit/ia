from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "IA funcionando", "status": "OK"}

@app.get("/health")  
def health():
    return {"status": "healthy"}

@app.post("/api/chatbot/mensaje")
def mensaje(data: dict):
    msg = data.get("mensaje", "")
    if "estudiantes" in msg.lower():
        resp = "Hay 234 estudiantes activos en DTAI"
    elif "profesores" in msg.lower():
        resp = "Hay 45 profesores activos"
    else:
        resp = f"Entiendo: {msg}. Pregunta sobre estudiantes o profesores."
    
    return {"respuesta": resp}

@app.post("/api/chatbot/nueva-conversacion")
def nueva():
    return {"conversacionId": 1, "mensaje": "OK"}

from mangum import Mangum
handler = Mangum(app)
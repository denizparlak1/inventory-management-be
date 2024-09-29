import webview
import threading
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.analytic import analytic_api
from api.auth import auth
from api.product import product_api
from db.db import Base, engine
from starlette.responses import FileResponse

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware ekliyoruz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik dosyalar (React build dosyaları)
app.mount("/static", StaticFiles(directory="static"), name="static")

# API router'ları ekliyoruz
app.include_router(auth.router, prefix="/api/authentication", tags=["auth"])
app.include_router(product_api.router, prefix="/api/product", tags=["product"])
app.include_router(analytic_api.router, prefix="/api/analytics", tags=["analytics"])

# React frontend'i serve ediyoruz
@app.get("/")
def serve_react_app():
    return FileResponse("static/index.html")

# Tüm diğer yolları index.html'e yönlendirme
@app.get("/{full_path:path}")
def catch_all(full_path: str):
    return FileResponse("static/index.html")


# FastAPI sunucusunu başlatma fonksiyonu
def start_fastapi():
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    # FastAPI sunucusunu bir thread içinde başlat
    threading.Thread(target=start_fastapi).start()

    # PyWebview ile masaüstü uygulaması aç
    webview.create_window("My FastAPI App", "http://127.0.0.1:8000")
    webview.start()

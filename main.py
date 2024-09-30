import webview
import threading
import uvicorn
import time
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


# Sunucunun durdurulmasını sağlamak için bir global değişken ekliyoruz
server_should_stop = False

# FastAPI sunucusunu başlatma fonksiyonu
def start_fastapi():
    # Log seviyesini debug olarak ayarlıyoruz
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, reload=False, log_level="debug")
    server = uvicorn.Server(config)

    while not server_should_stop:  # Sunucuyu manuel olarak durdurabiliriz
        server.run()
    server.should_exit = True

# PyWebView kapatıldığında tetiklenecek fonksiyon
def on_closed():
    global server_should_stop
    server_should_stop = True  # Sunucunun durmasını sağlayın

if __name__ == "__main__":
    # FastAPI sunucusunu bir thread içinde başlat
    server_thread = threading.Thread(target=start_fastapi)
    server_thread.start()

    # Sunucunun başlamasını bekliyoruz
    time.sleep(2)  # Sunucunun başlatılması için bekleme süresi

    # PyWebView ile masaüstü uygulaması aç
    window = webview.create_window("KAO STOK YÖNETİM", "http://127.0.0.1:8000")

    # Windows için 'cef' ya da 'mshtml' kullanabilirsiniz.
    webview.start(func=on_closed, gui='cef')  # Windows ortamında 'cef' kullanımı

    # Uygulama kapatıldığında thread'in kapanmasını sağla
    server_thread.join()

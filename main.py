import os
import shutil

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

app = FastAPI(debug=True)

# CORS middleware ekliyoruz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Statik dosyalar (React build dosyaları)
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# API router'ları ekliyoruz
app.include_router(auth.router, prefix="/api/authentication", tags=["auth"])
app.include_router(product_api.router, prefix="/api/product", tags=["product"])
app.include_router(analytic_api.router, prefix="/api/analytics", tags=["analytics"])


class API:
    def download_pdf(self, file_name):
        file_path = os.path.join(static_dir, file_name)
        if os.path.exists(file_path):
            save_path = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, file_name=file_name)
            if save_path:
                shutil.copy(file_path, save_path[0])
        else:
            print("Dosya bulunamadı:", file_path)


api = API()


# React frontend'i serve ediyoruz
@app.get("/")
def serve_react_app():
    index_file = os.path.join(static_dir, "index.html")
    return FileResponse(index_file)


@app.get("/logo")
async def get_logo():
    file_path = os.path.join("static", "logo.png")
    return FileResponse(file_path)


@app.get("/{full_path:path}")
def catch_all(full_path: str):
    index_file = os.path.join(static_dir, "index.html")
    return FileResponse(index_file)


# Sunucunun durdurulmasını sağlamak için bir global değişken ekliyoruz
server_should_stop = False


# FastAPI sunucusunu başlatma fonksiyonu
def start_fastapi():
    # Log seviyesini debug olarak ayarlıyoruz
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, reload=False, log_level="debug")
    server = uvicorn.Server(config)
    server.run()  # Döngü yerine sadece server.run()

    while not server_should_stop:  # Sunucuyu manuel olarak durdurabiliriz
        server.run()
    server.should_exit = True


# PyWebView kapatıldığında tetiklenecek fonksiyon
def on_closed():
    global server_should_stop
    server_should_stop = True  # Sunucunun durmasını sağlayın


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_fastapi)
    server_thread.start()

    time.sleep(2)

    # PyWebView ile masaüstü uygulaması aç
    window = webview.create_window("KAO STOK YÖNETİM", "http://127.0.0.1:8000", js_api=api)

    # Uygulama kapatıldığında PyWebView'in kapanma işlevini tanımla
    # Burada GUI motorunu manuel olarak belirliyoruz
    webview.start(func=on_closed, gui='edgechromium')  # 'cef', 'mshtml' veya 'edgechromium' deneyin

    # Uygulama kapatıldığında thread'in kapanmasını sağla
    server_thread.join()

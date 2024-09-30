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

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api/authentication", tags=["auth"])
app.include_router(product_api.router, prefix="/api/product", tags=["product"])
app.include_router(analytic_api.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/")
def serve_react_app():
    return FileResponse("static/index.html")


@app.get("/{full_path:path}")
def catch_all(full_path: str):
    return FileResponse("static/index.html")


server_should_stop = False


def start_fastapi():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, reload=False)
    server = uvicorn.Server(config)

    while not server_should_stop:
        server.run()
    server.should_exit = True


def on_closed():
    global server_should_stop
    server_should_stop = True


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_fastapi)
    server_thread.start()

    time.sleep(2)

    window = webview.create_window("KAO STOK YÖNETİM", "http://127.0.0.1:8000")

    webview.start(func=on_closed, gui='gtk')

    server_thread.join()

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


# Catch-all route: Diğer tüm istekleri index.html'e yönlendirme
@app.get("/{full_path:path}")
def catch_all(full_path: str):
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

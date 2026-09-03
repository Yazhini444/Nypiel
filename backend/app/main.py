import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models, inference
from .database import engine
from .routers import auth_router, scan_router, chat_router

models.Base.metadata.create_all(bind=engine)
os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="nypiel API", description="Skin type & concern analysis API for nypiel.")

app.add_middleware(
    CORSMiddleware,
    # Lock this down to your real frontend origin(s) before going live.
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router.router)
app.include_router(scan_router.router)
app.include_router(chat_router.router)


@app.on_event("startup")
def startup():
    print("[nypiel] Server started. Models will load on first request.")


@app.get("/")
def root():
    return {"status": "ok", "service": "nypiel API"}

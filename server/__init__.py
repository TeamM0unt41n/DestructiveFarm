from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from server.api import client_router
from server.views import view_router

app = FastAPI()

app.add_middleware(CORSMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(client_router)
app.include_router(view_router)
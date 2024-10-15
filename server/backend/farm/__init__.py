from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from farm.api import client_router
from farm.views import view_router
from farm.submit_loop import submit

async def lifespan(app:FastAPI):
    await submit()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware)

app.mount("/static", StaticFiles(directory="farm/static"), name="static")

app.include_router(client_router)
app.include_router(view_router)
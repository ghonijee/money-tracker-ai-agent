from dotenv import load_dotenv
from fastapi import FastAPI
from src.controllers import message_controller

load_dotenv()

app = FastAPI();
app.include_router(message_controller.router, prefix="/api/v1", tags=["message"])
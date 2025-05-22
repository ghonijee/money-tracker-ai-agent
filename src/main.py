from dotenv import load_dotenv
from fastapi import FastAPI
from src.controllers import message_controller, whatapps_hook_controller

load_dotenv()

app = FastAPI()
VERIFY_TOKEN = "your_verify_token"


@app.get("/")
def read_root():
	return {"Hello": "World dunia"}


app.include_router(message_controller.router, prefix="/api/v1", tags=["message"])
app.include_router(whatapps_hook_controller.router, prefix="/api/v1", tags=["whatsapp"])

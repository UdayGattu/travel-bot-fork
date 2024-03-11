from fastapi import FastAPI,Form,Request,Depends,HTTPException
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()
Base.metadata.create_all(bind=engine)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_path = os.path.join(BASE_DIR, "frontend", "templates")
templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class Message(BaseModel):
    user_message: str
    user_id: Optional[int] = None
def chatbot_response(user_message: str) -> str:
    # Implement your chatbot logic here
    # For demonstration, echoing back the user message
    return f"Echo: {user_message}"

@app.get('/',response_class=HTMLResponse)
async def read_root(request:Request):
    return templates.TemplateResponse('index.html',{"request":request})

@app.post("/send-message/")
async def send_message(message: Message):
    response_message = chatbot_response(message.user_message)
    return {"response": response_message, "your_message": message.user_message}
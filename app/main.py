from fastapi import FastAPI,Form,Request,Depends,HTTPException,status
from typing import Optional,Annotated
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models
from database import engine,Sessionlocal
import os


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_path = os.path.join(BASE_DIR, "frontend", "templates")
templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")




def get_db():
    db=Sessionlocal()
    try:
        yield db
        
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]



# class Message(BaseModel):
#     user_message: str
#     user_id: Optional[int] = None
# def chatbot_response(user_message: str) -> str:
#     # Implement your chatbot logic here
#     # For demonstration, echoing back the user message
#     return f"Echo: {user_message}"

@app.get('/',response_class=HTMLResponse)
async def read_root(request:Request):
    return templates.TemplateResponse('index.html',{"request":request})

# @app.post("/send-message/")
# async def send_message(message: Message):
#     response_message = chatbot_response(message.user_message)
#     return {"response": response_message, "your_message": message.user_message}

# @app.post('/users/',status_code=status.HTTP_201_CREATED)
# async def create_user(user:UserBase,db:db_dependency):
#     db_user = models.User(**user.model_dump())
#     db.add(db_user)
#     db.commit()
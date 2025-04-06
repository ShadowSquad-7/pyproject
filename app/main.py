from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.users import routers as user_rout

app = FastAPI()
app.include_router(user_rout.router)

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("MainPage.html", {"request": request})
